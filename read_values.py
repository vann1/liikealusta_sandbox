from setup_logging import setup_logging
from pymodbus.client import ModbusTcpClient
import time
from websocket_client import WebsocketClient
import asyncio
from utils import extract_part
from test import bit_high_low


class ReadValues():
    SERVER_URL = "http://127.0.0.1:5001/"
    SERVER_IP_LEFT="192.168.0.211"
    SERVER_IP_RIGHT="192.168.0.212"
    SERVER_PORT=502
    client_left = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
    client_right = ModbusTcpClient(host=SERVER_IP_RIGHT, port=SERVER_PORT)
    client_right.connect()
    client_left.connect()
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
        
    def read_register(self):
        try:
            registers_file = open("registers.txt", "w")

            # Factory BoardTempTripLevel BTMP16
            response_left = self.client_left.read_holding_registers(address=9202, count=1)
            response_right = self.client_right.read_holding_registers(address=9202, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 5)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 5)
            registers_file.write(f"""Factory BoardTempTripLevel BTMP16:
                            \nLeft_motor:{response_left_high}.{response_left_low}
                            \nRight_motor:{response_right_high}.{response_right_low}\n\n""")

            # Factory IPEAK UCUR16
            response_left = self.client_left.read_holding_registers(address=9204, count=1)
            response_right = self.client_right.read_holding_registers(address=9204, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 7)
            registers_file.write(f"""Factory IPEAK UCUR16:
                            \nLeft_motor:{response_left_high}.{response_left_low}
                            \nRight_motor:{response_right_high}.{response_right_low}\n\n""")

            # Factory Icontinious UCUR16
            response_left = self.client_left.read_holding_registers(address=9205, count=1)
            response_right = self.client_right.read_holding_registers(address=9205, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 7)
            registers_file.write(f"""Factory Icontinious UCUR16:
                            \nLeft_motor:{response_left_high}.{response_left_low}
                            \nRight_motor:{response_right_high}.{response_right_low}\n\n""")

            # Factory ActuatorTempTripLevel ATMP16
            response_left = self.client_left.read_holding_registers(address=9209, count=1)
            response_right = self.client_right.read_holding_registers(address=9209, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 3)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 3)
            registers_file.write(f"""Factory ActuatorTempTripLevel ATMP16:
                            \nLeft_motor:{response_left_high}.{response_left_low}
                            \nRight_motor:{response_right_high}.{response_right_low}\n\n""")

            # bandwidth
            response_left = self.client_left.read_holding_registers(address=7201, count=1)
            response_right = self.client_right.read_holding_registers(address=7201, count=1)
            registers_file.write(f"""bandwidth:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            response_left = self.client_left.read_holding_registers(address=7231, count=1)
            response_right = self.client_right.read_holding_registers(address=7231, count=1)
            registers_file.write(f"""bandwidth 7231:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # I peak IPEAK - 2560
            response_left = self.client_left.read_holding_registers(address=5108, count=1)
            response_right = self.client_right.read_holding_registers(address=5108, count=1)
            registers_file.write(f"""I peak IPEAK - 2560:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            response_left = self.client_left.read_holding_registers(address=9205, count=1)
            response_right = self.client_right.read_holding_registers(address=9205, count=1)
            registers_file.write(f"""Register 9205:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # Current operation mode
            response_left = self.client_left.read_holding_registers(address=31, count=1)
            response_right = self.client_right.read_holding_registers(address=31, count=1)
            registers_file.write(f"""Current operation mode:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # analog input parameters options
            response_left = self.client_left.read_holding_registers(address=31, count=1)
            response_right = self.client_right.read_holding_registers(address=31, count=1)
            registers_file.write(f"""analog input parameters options:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # current revolutions
            response_left = self.client_left.read_holding_registers(address=378, count=2)
            response_right = self.client_right.read_holding_registers(address=378, count=2)
            registers_file.write(f"""current revolutions:
                            \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                            \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}\n\n""")

            # host control command mode
            response_left = self.client_left.read_holding_registers(address=4303, count=1)
            response_right = self.client_right.read_holding_registers(address=4303, count=1)
            registers_file.write(f"""host control command mode:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # analog i channel
            response_left = self.client_left.read_holding_registers(address=7101, count=1)
            response_right = self.client_right.read_holding_registers(address=7101, count=1)
            registers_file.write(f"""analog i channel:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # alt command mode
            response_left = self.client_left.read_holding_registers(address=5107, count=1)
            response_right = self.client_right.read_holding_registers(address=5107, count=1)
            registers_file.write(f"""alt command mode:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # defaul modet
            response_left = self.client_left.read_holding_registers(address=5106, count=1)
            response_right = self.client_right.read_holding_registers(address=5106, count=1)
            registers_file.write(f"""defaul modet:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # IEG MODE
            response_left = self.client_left.read_holding_registers(address=4316, count=1)
            response_right = self.client_right.read_holding_registers(address=4316, count=1)
            registers_file.write(f"""IEG MODE:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # IEG MOTION
            response_left = self.client_left.read_holding_registers(address=4317, count=1)
            response_right = self.client_right.read_holding_registers(address=4317, count=1)
            registers_file.write(f"""IEG MOTION:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # ANALOG POS MIN
            response_left = self.client_left.read_holding_registers(address=7102, count=2)
            response_right = self.client_right.read_holding_registers(address=7102, count=2)
            registers_file.write(f"""ANALOG POS MIN:
                            \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                            \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}\n\n""")

            # ANALOG POS MAX
            response_left = self.client_left.read_holding_registers(address=7104, count=2)
            response_right = self.client_right.read_holding_registers(address=7104, count=2)
            registers_file.write(f"""ANALOG POS MAX:
                            \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                            \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}\n\n""")

            # VELOCITY 
            response_left = self.client_left.read_holding_registers(address=7106, count=2)
            response_right = self.client_right.read_holding_registers(address=7106, count=2)
            registers_file.write(f"""VELOCITY:
                            \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                            \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}\n\n""")

            # ACCEL
            response_left = self.client_left.read_holding_registers(address=7108, count=2)
            response_right = self.client_right.read_holding_registers(address=7108, count=2)
            registers_file.write(f"""ACCEL:
                            \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                            \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}\n\n""")

            # MODBUSCNTRL
            response_left = self.client_left.read_holding_registers(address=7188, count=1)
            response_right = self.client_right.read_holding_registers(address=7188, count=1)
            registers_file.write(f"""MODBUSCNTRL:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # OEG sttus
            response_right = self.client_right.read_holding_registers(address=104, count=1)
            response_left = self.client_left.read_holding_registers(address=104, count=1)
            test1 = bin(response_left.registers[0])
            test2 = bin(response_right.registers[0])
            registers_file.write(f"""OEG sttus:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")

            # home position
            response_left = self.client_left.read_holding_registers(address=6002, count=2)
            response_right = self.client_right.read_holding_registers(address=6002, count=2)
            registers_file.write(f"""home position:
                            \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                            \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}\n\n""")

            # I peak factory
            response_left = self.client_left.read_holding_registers(address=9204, count=1)
            response_right = self.client_right.read_holding_registers(address=9204, count=1)
            registers_file.write(f"""I peak factory:
                            \nLeft_motor:{response_left.registers[0]}
                            \nRight_motor:{response_right.registers[0]}\n\n""")
        finally:
            registers_file.close()
                
    async def init(self):
        self.logger = setup_logging("read_telemetry", "read_telemetry.txt")
        self.wsclient = WebsocketClient(self.logger, on_message=self.on_message)
        self.BTfile = open("BoardTemp.txt", "w")
        self.ATfile = open("ActuatorTemp.txt", "w")
        self.ICfile = open("IContinous.txt", "w")
        await self.wsclient.connect()
        
    async def main(self):
        try:
            # await self.init()
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
    # asyncio.run(main())
    readValues = ReadValues()
    readValues.read_register()