import asyncio
import websockets
from websockets.exceptions import ConnectionClosed
from config import Config

config = Config()

class WebsocketClient():
    def __init__(self, logger, identity="unknown", uri=f"ws://localhost:{config.WEBSOCKET_SRV_PORT}", on_message=None, reconnect_interval=2.5, max_reconnect_attempt=10,on_message_async=False):
        self.uri = uri
        self.on_message_async = on_message_async
        self.socket = None
        self.is_running = False
        self.on_message = on_message
        self._listen_task = None
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempt = max_reconnect_attempt
        self.reconnect_count = 0
        self.logger = logger
        self.identity = identity
        self._connection_lock = asyncio.Lock()  # Add lock for connection operations
        self._reconnecting = False  # Prevent multiple reconnection attempts
        
    async def connect(self):
        async with self._connection_lock:  # Protect connection operations
            try:
                if self.is_running:
                    self.logger.info("Client is already connected, can't connect again")
                    return 
                
                if self._reconnecting:
                    self.logger.info("Reconnection already in progress")
                    return
                
                # Clean up any existing connection
                await self._cleanup_connection()
                
                self.socket = await websockets.connect(
                    self.uri,
                    ping_interval=None,  # Disable automatic ping
                    ping_timeout=None    # Disable ping timeout
                )
                await self.socket.send(f"action=identify|identity={self.identity}|")
                self.is_running = True
                self.reconnect_count = 0
                self._reconnecting = False
                self.logger.info(f"client connected to server: {self.uri}")
                if self.on_message:
                    if self.on_message_async:
                        await self.on_message(f"event=connected|message=Client connected to server.|")
                    else:
                        self.on_message(f"event=connected|message=Client connected to server.|")

                
                # Create new listen task
                self._listen_task = asyncio.create_task(self._listen())
                
            except asyncio.TimeoutError:
                await self.handle_connection_failure(f"Connection timed out")
            except Exception as e:
                await self.handle_connection_failure(f"Error connecting to the server: {e}")
    
    async def handle_connection_failure(self, error_msg):
        """Handle a connection failure by scheduling a reconnect or closing the client."""
        async with self._connection_lock:
            self.logger.error(f"Connection failed: {error_msg}")
            self.is_running = False
            
            if self._reconnecting:
                return  # Already handling reconnection
                
            self.reconnect_count += 1
            if self.reconnect_count < self.max_reconnect_attempt:
                self._reconnecting = True
                # Schedule reconnect without blocking
                asyncio.create_task(self._schedule_reconnect())
            else:
                self.logger.info("Maximum reconnect attempts reached, closing client")
                await self._cleanup_connection()

    async def _listen(self):
        try:
            self.logger.info("Creating listening coroutine for client")
            while self.is_running and self.socket:
                try:
                    response = await self.socket.recv()
                    if self.on_message:
                        if self.on_message_async:
                            await self.on_message(response)
                        else:
                            self.on_message(response)
                except ConnectionClosed:
                    self.logger.info("Client disconnected from the server")
                    break
                except Exception as e:
                    self.logger.error(f"Error receiving message: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Exception in the listen coroutine: {e}")
        finally:
            # Only trigger reconnection if we were supposed to be running
            if self.is_running and not self._reconnecting:
                await self.handle_connection_failure("Listen coroutine ended unexpectedly")

    async def _schedule_reconnect(self):
        """Schedule a reconnection attempt after a delay."""
        try:
            await asyncio.sleep(self.reconnect_interval)
            if self._reconnecting:  # Only reconnect if still in reconnecting state
                await self.connect()
        except Exception as e:
            self.logger.error(f"Error during reconnection: {e}")
            self._reconnecting = False

    async def send(self, message):
        try:
            if not self.is_running or not self.socket:
                self.logger.info("Client not connected, can't send a message")
                return False

            await self.socket.send(message)
            return True
        except ConnectionClosed:
            self.logger.warning("Connection closed while sending message")
            await self.handle_connection_failure("Connection closed during send")
            return False
        except Exception as e:
            self.logger.error(f"Error while client was sending a message: {e}")
            await self.handle_connection_failure(f"Send error: {e}")
            return False

    async def _cleanup_connection(self):
        """Clean up existing connection and tasks."""
        # Cancel and wait for listen task
        if self._listen_task and not self._listen_task.done():
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None

        # Close socket
        if self.socket:
            try:
                await self.socket.close()
            except Exception as e:
                self.logger.error(f"Error closing socket: {e}")
            finally:
                self.socket = None

    async def close(self):
        """Close the websocket connection and clean up resources."""
        async with self._connection_lock:
            try:
                self.is_running = False
                self._reconnecting = False
                await self._cleanup_connection()
                self.logger.info("Client socket closed")
            except Exception as e:
                self.logger.error(f"Exception while closing client: {e}")

    async def wait_for_connection(self, timeout=10):
        """Wait for the client to be connected, useful for testing."""
        start_time = asyncio.get_event_loop().time()
        while not self.is_running and (asyncio.get_event_loop().time() - start_time) < timeout:
            await asyncio.sleep(0.1)
        return self.is_running