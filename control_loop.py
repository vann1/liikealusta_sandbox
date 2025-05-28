import NiDAQ_controller
import time
import requests
import asyncio
from setup_logging import setup_logging
from pymodbus.client import ModbusTcpClient
import time
from websocket_client import WebsocketClient
import asyncio
from utils import extract_part
from test import bit_high_low


class ControlLoop():
    joy = NiDAQ_controller.NiDAQJoysticks()
    MAX_ROLL = 16
    MAX_PITCH = 8.5
    MAX_DIFF = 0.2
    logger = None
    wsclient = None
    asd = True
    async def init(self):
        self.logger = setup_logging("control_loop", "control_loop.txt")
        self.wsclient = WebsocketClient(self.logger)
        await self.wsclient.connect()
        a = 10
    async def main(self):
        await self.init()
        while True:
            try:
                await asyncio.sleep(0.05)
                values = self.joy.read()
                pitch = values[4] * (-1)
                roll = values[3] * (-1)
                button_pressed = values[18]

                if button_pressed == 1.0:
                    print("button pressed!")
                    roll = roll * self.MAX_ROLL
                    pitch = pitch * self.MAX_PITCH
                    roll_has_val = abs(roll) > self.MAX_DIFF
                    pitch_has_val = abs(pitch) > self.MAX_DIFF

                    if not roll_has_val:
                        roll = 0.0
                    if not pitch_has_val:
                        pitch = 0.0

                    ### make a command
                    await self.wsclient.send(f"action=rotate|pitch={pitch}|roll={roll}|")
            except Exception as e:
                print(e)
                continue
            
if __name__ == "__main__":
    controlLoop = ControlLoop()
    asyncio.run(controlLoop.main())