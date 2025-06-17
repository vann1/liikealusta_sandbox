from websocket_client import WebsocketClient
import asyncio

class ServerSpammingTest():
    
    def __init__(self):
        self.client1 = None
        self.client2 = None
        self.client3 = None
        self.client4 = None
        self.client5 = None
        
    async def create_5_clients(self):
            self.client1 = WebsocketClient()
            self.client2 = WebsocketClient()
            self.client3 = WebsocketClient()
            self.client4 = WebsocketClient()
            self.client5 = WebsocketClient()
            await self.client1.connect()
            await self.client2.connect()
            await self.client3.connect()
            await self.client4.connect()
            await self.client5.connect()

    async def spam(client):
        while True:
            await client.send(f"action=rotate|pitch={0}|roll={0}|")
            await asyncio.sleep((1/20))
    
    async def main(self):
        await self.create_5_clients()
        await asyncio.gather(self.spam(self.client1),
                             self.spam(self.client2),
                             self.spam(self.client3),
                             self.spam(self.client4),
                             self.spam(self.client5))

 
            
if __name__ == "__main__":
    sst = ServerSpammingTest()
    asyncio.run(sst.main())