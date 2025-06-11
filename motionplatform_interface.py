from websocket_client import WebsocketClient
from setup_logging import setup_logging
import utils as utils

class MotionPlatform_Interface():
    def __init__(self):
        self.error = False
        
    async def init(self):
        """
        Initializes logger for motionplatform_interface class and WebsocketClient object.
        Connects to websocket server.
        """
        self.logger = setup_logging("motionplatform_interface", "motionplatform_interface.log")
        self.wsclient = WebsocketClient(self.logger, identity="interface", on_message=self.handle_client_message)
        await self.wsclient.connect()

    def handle_client_message(self, message):
        """
        Handles messages recevied from server.
        """
        event = utils.extract_part("event=", message=message)
        clientmessage = utils.extract_part("message=", message=message)
        if not event:
            self.logger.error("No event specified in message.")
            return 
        if not clientmessage: 
            self.logger.error("No client message specified in message.")
            return
        elif event == "error":
            self.error = clientmessage
            

    async def rotate(self,pitch,roll):
        """
        Takes parameters pitch and roll and rotates motionplatform accordingly with given values.
        Raises ValueError if rotate frequency is too fast.
        """
        if self.error:
            self.logger.error(f"Error rotating motionplatform. Error: {self.error}")
            raise ValueError(f"Error rotating motionplatform. Error: {self.error}")
        await self.wsclient.send(f"action=rotate|pitch={pitch}|roll={roll}|")



    
    
        
        