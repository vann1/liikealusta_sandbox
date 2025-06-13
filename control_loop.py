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
from motionplatform_interface import MotionPlatform_Interface


class ControlLoop():
    
    def __init__(self):
        self.interface_test = MotionPlatform_Interface()
        self.joy = NiDAQ_controller.NiDAQJoysticks()
        self.MAX_PITCH = 8.5
        self.MAX_ROLL = 8.5
        self.MAX_DIFF = 0.2
        self.logger = None
        self.wsclient = None
        self.asd = True
        
    async def main(self):
        await self.interface_test.init()
        while True:
            try:
                await asyncio.sleep(0.1)
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
                    await self.interface_test.rotate(pitch=pitch,roll=roll)
            except Exception as e:
                print(e)
                continue
            
            
if __name__ == "__main__":
    controlLoop = ControlLoop()
    asyncio.run(controlLoop.main())