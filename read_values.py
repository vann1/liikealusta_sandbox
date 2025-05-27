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
                registers = open("registers.txt", "w")

                #Factory BoardTempTripLevel BTMP16
                response_left = self.client_left.read_holding_registers(address=9202, count=1)
                response_right = self.client_right.read_holding_registers(address=9202, count=1)
                response_left_high, response_left_low = bit_high_low(response_left.registers[0],5)
                response_right_high, response_right_low = bit_high_low(response_right.registers[0],5)
                registers.write(f"""Factory BoardTempTripLevel BTMP16:
                                \nLeft_motor:{response_left_high}.{response_left_low}
                                \nRight_motor:{response_right_high}.{response_right_low}""")

                #Factory IPEAK UCUR16
                response_left = self.client_left.read_holding_registers(address=9204, count=1)
                response_right = self.client_right.read_holding_registers(address=9204, count=1)
                response_left_high, response_left_low = bit_high_low(response_left,7)
                response_right_high, response_right_low = bit_high_low(response_right,7)
                
                #Factory Icontinious UCUR16
                response_left = self.client_left.read_holding_registers(address=9205, count=1)
                response_right = self.client_right.read_holding_registers(address=9205, count=1)
                response_left_high, response_left_low = bit_high_low(response_left,7)
                response_right_high, response_right_low = bit_high_low(response_right,7)
                
                #Factory ActuatorTempTripLevel ATMP16
                response_left = self.client_left.read_holding_registers(address=9209, count=1)
                response_right = self.client_right.read_holding_registers(address=9209, count=1)
                response_left_high, response_left_low = bit_high_low(response_left,3)
                response_right_high, response_right_low = bit_high_low(response_right,3)
                
                
                #bandwidth
                response_left = self.client_left.read_holding_registers(address=7201, count=1)
                response_left = self.client_left.read_holding_registers(address=7231, count=1)

                #IPEAK - 2560 
                response_left = self.client_left.read_holding_registers(address=5108, count=1)
                response_right = self.client_right.read_holding_registers(address=5108, count=1)

                # Current operation mode
                response_left = self.client_left.read_holding_registers(address=31, count=1)
                response_right = self.client_right.read_holding_registers(address=31, count=1)
                registers.write(f"""Current operation mode:
                                \nLeft_motor:{response_left.registers[0]}
                                \nRight_motor:{response_right.registers[0]}""")


                ### analog input parameters options
                response_left = self.client_left.read_holding_registers(address=31, count=1)
                response_right = self.client_right.read_holding_registers(address=31, count=1)


                #### analog min min range
                response_left = self.client_left.read_holding_registers(address=7218, count=2)
                response_right = self.client_right.read_holding_registers(address=7218, count=2) 
                registers.write(f"""Factory BoardTempTripLevel BTMP16:
                                \nLeft_motor:{response_left.registers[0]}.{response_left.registers[1]}
                                \nRight_motor:{response_right.registers[0]}.{response_right.registers[1]}""")


                ### user mode 2 analog in min
                response_left = self.client_left.read_holding_registers(address=7210, count=2)
                response_right = self.client_right.read_holding_registers(address=7210, count=2) 

                ### user mode 2 analog in max
                response_left = self.client_left.read_holding_registers(address=7212, count=2)
                response_right = self.client_right.read_holding_registers(address=7212, count=2) 

                ### analog max range
                response_left = self.client_left.read_holding_registers(address=7220, count=2)
                response_right = self.client_right.read_holding_registers(address=7220, count=2) 

                  ### analog min adc range
                response_left = self.client_left.read_holding_registers(address=7214, count=2)
                response_right = self.client_right.read_holding_registers(address=7214, count=2)

                ### analog max adc range
                ### 15900
                response_left = self.client_left.read_holding_registers(address=7216, count=2)
                response_right = self.client_right.read_holding_registers(address=7216, count=2) 

                # current revolutions
                response_left = self.client_left.read_holding_registers(address=378, count=2)
                response_right = self.client_right.read_holding_registers(address=378, count=2) 

                # host control command mode
                response_left = self.client_left.read_holding_registers(address=4303, count=1)
                response_right = self.client_right.read_holding_registers(address=4303, count=1) 

                # analog i channel
                response_left = self.client_left.read_holding_registers(address=7101, count=1)
                response_right = self.client_right.read_holding_registers(address=7101, count=1) 

                # alt command mode
                response_left = self.client_left.read_holding_registers(address=5107, count=1)
                response_right = self.client_right.read_holding_registers(address=5107, count=1)

                 # defaul modet
                response_left = self.client_left.read_holding_registers(address=5106, count=1)
                response_right = self.client_right.read_holding_registers(address=5106, count=1)

                # IEG MODE
                response_left = self.client_left.read_holding_registers(address=4316, count=1) 
                response_right = self.client_right.read_holding_registers(address=4316, count=1)

                # IEG MOTION
                response_left = self.client_left.read_holding_registers(address=4317, count=1) 
                response_right = self.client_right.read_holding_registers(address=4317, count=1)

                #ANALOG POS MIN
                response_left = self.client_left.read_holding_registers(address=7102, count=2) 
                response_right = self.client_right.read_holding_registers(address=7102, count=2) 

                # ANALOG POS MAX
                response_left = self.client_left.read_holding_registers(address=7104, count=2)
                response_right = self.client_right.read_holding_registers(address=7104, count=2)

                 # VELOCITY 213 - 256
                response_left = self.client_left.read_holding_registers(address=7106, count=2)
                response_right = self.client_right.read_holding_registers(address=7106, count=2)
                
                # ACCEL
                response_left = self.client_left.read_holding_registers(address=7108, count=2) 
                response_right = self.client_right.read_holding_registers(address=7108, count=2)

                 # MODBUSCNTRL
                response_left = self.client_left.read_holding_registers(address=7188, count=1)
                response_right = self.client_right.read_holding_registers(address=7188, count=1)

                # self.client_left.write_register(address=7188, value=3000)

                # OEG sttus
                response_right = self.client_right.read_holding_registers(address=104, count=1)
                response_left = self.client_right.read_holding_registers(address=104, count=1)
                test1 = bin(response_left.registers[0])
                test2 = bin(response_right.registers[0])

                # home åpsition
                response_left = self.client_right.read_holding_registers(address=6002, count=2)
                response_right = self.client_right.read_holding_registers(address=6002, count=2)

                 # I peak factory
                response_left = self.client_left.read_holding_registers(address=9204, count=1)
                response_right = self.client_right.read_holding_registers(address=9204, count=1)
        finally:
            registers.close()
            
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