import NiDAQ_controller
import requests
import asyncio
from setup_logging import setup_logging
from pymodbus.client import ModbusTcpClient
import time

import asyncio
from utils import extract_part
from test import bit_high_low
from motionplatform_interface import MotionPlatformInterface


class ControlLoop():
    
    def __init__(self):
        self.mpi = MotionPlatformInterface()
        self.joy = NiDAQ_controller.NiDAQJoysticks()
        self.MAX_PITCH = 10
        self.MAX_ROLL = 20
        self.MAX_DIFF = 0
        self.logger = None
        self.wsclient = None
        self.asd = True
        
    def main(self):
        self.mpi.init()
        while True:
            try:
                time.sleep(1/1000)
                values = self.joy.read()
                pitch = values[4] * (-1)
                roll = values[3]
                button_pressed = values[18]

                if button_pressed == 1.0:
                    # print("button pressed!")
                    roll = roll * self.MAX_ROLL
                    pitch = pitch * self.MAX_PITCH
                    roll_has_val = abs(roll) > self.MAX_DIFF
                    pitch_has_val = abs(pitch) > self.MAX_DIFF

                    if not roll_has_val:
                        roll = 0.0
                    if not pitch_has_val:
                        pitch = 0.0

                    ### make a command
                    self.mpi.set_angles(pitch=pitch,roll=roll)
            except ValueError:
                break
            
            except Exception as e:
                print(e)
                continue
            
            
if __name__ == "__main__":
    controlLoop = ControlLoop()
    controlLoop.main()