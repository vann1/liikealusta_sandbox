from setup_logging import setup_logging
from pymodbus.client import ModbusTcpClient
import time
from websocket_client import WebsocketClient
import asyncio
from utils import extract_part


class ReadValues():
    SERVER_URL = "http://127.0.0.1:5001/"
    SERVER_IP_LEFT="192.168.0.211"
    SERVER_IP_RIGHT="192.168.0.212"
    SERVER_PORT=502
    client_leFt = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
    client_right = ModbusTcpClient(host=SERVER_IP_RIGHT, port=SERVER_PORT)
    client_right.connect()
    client_leFt.connect()
    logger = None
    wsclient = None

    
    def on_message(self,msg):
        event = extract_part("event=",msg)
        message = extract_part("message=",msg)
        if not message:
            self.logger.error("Message part missing")
            return
        if event == "telemetrydata":
            self.boardtemp = extract_part("boardtemp:", message, delimiter="*")
            self.actuatortemp = extract_part("actuatortemp:",message,delimiter="*")
            self.ic = extract_part("IC:",message,delimiter="*")
            self.BTfile.write(f"{self.boardtemp}\n")
            self.ATfile.write(f"{self.actuatortemp}\n")
            self.ICfile.write(f"{self.ic}\n")
        
    
    async def init(self):
        self.logger = setup_logging("read_telemetry", "read_telemetry.txt")
        self.wsclient = WebsocketClient(self.logger, on_message=self.on_message)
        self.BTfile = open("BoardTemp.txt", "w")
        self.ATfile = open("ActuatorTemp.txt", "w")
        self.ICfile = open("IContinous.txt", "w")
        await self.wsclient.connect()
        
        
    async def main(self):
        try:
            await self.init()
            while True:
                self.wsclient.send("action=readtelemetry|")
                time.sleep(0.1)
        except Exception as e:
            print(f"Error while reading registers: {e}")
        finally: 
            self.BTfile.close()
            self.ATfile.close()
            self.ICfile.close()

    if __name__ == "__main__":
        asyncio.run(main())