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
    asd = True
    
    async def on_message(self,msg):
        
        event = extract_part("event=",msg)
        message = extract_part("message=",msg)
        if not message:
            self.logger.error("Message part missing")
            return
        if event == "telemetrydata":
            self.boardtemp = extract_part("boardtemp:", message, delimiter="*")
            self.actuatortemp = extract_part("actuatortemp:",message,delimiter="*")
            self.VBUS = extract_part("VBUS:", message, delimiter="*")
            self.ic = extract_part("IC:",message,delimiter="*")
            self.BTfile.write(f"{self.boardtemp}\n")
            self.ATfile.write(f"{self.actuatortemp}\n")
            self.ICfile.write(f"{self.ic}\n")
            self.VBUSfile.write(f"{self.VBUS}\n")
            self.asd = False
            await self.wsclient.close()
    def write_to_file(self, file, title, left_vals, right_vals):
        left_vals = ".".join([str(val) for val in left_vals])
        right_vals = ".".join([str(val) for val in right_vals])
            
        file.write(f"""
            #### - {title} - ####
            Left motor: {left_vals}
            Right motor: {right_vals}
            """)
    
    def read_register(self):
        try:
            registers_file = open("registers.txt", "w")

            # Factory BoardTempTripLevel BTMP16 - 11.5
            response_left = self.client_left.read_holding_registers(address=9202, count=1)
            response_right = self.client_right.read_holding_registers(address=9202, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 5)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 5)
            
            self.write_to_file(file=registers_file, title="Factory BoardTempTripLevel BTMP16", left_vals=[response_left_high], right_vals=[response_right_high])

            # Factory IPEAK UCUR16
            response_left = self.client_left.read_holding_registers(address=9204, count=1)
            response_right = self.client_right.read_holding_registers(address=9204, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 7)
            self.write_to_file(registers_file, title="Factory IPEAK UCUR16:", left_vals=[response_left_high], right_vals=[response_right_high])

            # Factory Icontinious UCUR16
            response_left = self.client_left.read_holding_registers(address=9205, count=1)
            response_right = self.client_right.read_holding_registers(address=9205, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 7)
            self.write_to_file(registers_file, title="Factory Icontinious UCUR16:", left_vals=[response_left_high], right_vals=[response_right_high])
            
            # Factory ActuatorTempTripLevel ATMP16 - 13.3
            response_left = self.client_left.read_holding_registers(address=9209, count=1)
            response_right = self.client_right.read_holding_registers(address=9209, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 3)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 3)
            self.write_to_file(registers_file, title="Factory ActuatorTempTripLevel ATMP16:", left_vals=[response_left_high], right_vals=[response_right_high])

            # HOME PRIMARY OPTIONS FLAG MAP - 
            response_left = self.client_left.read_holding_registers(address=6414, count=1)
            response_right = self.client_right.read_holding_registers(address=614, count=1)
            self.write_to_file(registers_file, title="HOME PRIMARY OPTIONS FLAG MAP -:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Factory LowVoltageTripLevel UVOLT16 - 11.5
            response_left = self.client_left.read_holding_registers(address=9200, count=1)
            response_right = self.client_right.read_holding_registers(address=9200, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 5)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 5)
            decimal_normalized_left = response_left_low / UVOLT16_DECIMAL_MAX
            decimal_normalized_right = response_right_low / UVOLT16_DECIMAL_MAX
            self.write_to_file(registers_file, title="LowVoltageTripLevel:", left_vals=[response_left_high, decimal_normalized_right], right_vals=[response_right_high, decimal_normalized_right])

            # Factory HighVoltageTripLevel UVOLT16 - 11.5
            UVOLT16_DECIMAL_MAX = 2**5
            response_left = self.client_left.read_holding_registers(address=9201, count=1)
            response_right = self.client_right.read_holding_registers(address=9201, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 5)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 5)
            decimal_normalized_left = response_left_low / UVOLT16_DECIMAL_MAX
            decimal_normalized_right = response_right_low / UVOLT16_DECIMAL_MAX

            self.write_to_file(registers_file, title="HighVoltageTripLevel:", left_vals=[response_left_high, decimal_normalized_left], right_vals=[response_right_high, decimal_normalized_right])

            # User defined IPEAK - 2560
            response_left = self.client_left.read_holding_registers(address=5108, count=1)
            response_right = self.client_right.read_holding_registers(address=5108, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 7)
            self.write_to_file(registers_file, title="User defined IPEAK - 2560:", left_vals=[response_left_high], right_vals=[response_right_high])

            # Current operation mode
            response_left = self.client_left.read_holding_registers(address=31, count=1)
            response_right = self.client_right.read_holding_registers(address=31, count=1)
            self.write_to_file(registers_file, title="Current operation mode:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # current revolutions
            response_left = self.client_left.read_holding_registers(address=378, count=2)
            response_right = self.client_right.read_holding_registers(address=378, count=2)
            self.write_to_file(registers_file, title="current revolutions:", left_vals=[response_left.registers[1], response_left.registers[0]], right_vals=[response_right.registers[1], response_right.registers[0]])

            # host control command mode
            response_left = self.client_left.read_holding_registers(address=4303, count=1)
            response_right = self.client_right.read_holding_registers(address=4303, count=1)
            self.write_to_file(registers_file, title="host control command mode:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # analog i channel
            response_left = self.client_left.read_holding_registers(address=7101, count=1)
            response_right = self.client_right.read_holding_registers(address=7101, count=1)
            self.write_to_file(registers_file, title="analog i channel:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # alt command mode
            response_left = self.client_left.read_holding_registers(address=5107, count=1)
            response_right = self.client_right.read_holding_registers(address=5107, count=1)
            self.write_to_file(registers_file, title="alt command mode:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # default mode
            response_left = self.client_left.read_holding_registers(address=5106, count=1)
            response_right = self.client_right.read_holding_registers(address=5106, count=1)
            self.write_to_file(registers_file, title="default mode:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # IEG MODE
            response_left = self.client_left.read_holding_registers(address=4316, count=1)
            response_right = self.client_right.read_holding_registers(address=4316, count=1)
            self.write_to_file(registers_file, title="IEG MODE:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # IEG MOTION
            response_left = self.client_left.read_holding_registers(address=4317, count=1)
            response_right = self.client_right.read_holding_registers(address=4317, count=1)
            self.write_to_file(registers_file, title="IEG MOTION:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # ANALOG POS MIN
            response_left = self.client_left.read_holding_registers(address=7102, count=2)
            response_right = self.client_right.read_holding_registers(address=7102, count=2)
            self.write_to_file(registers_file, title="ANALOG POS MIN:", left_vals=[response_left.registers[0], response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # ANALOG POS MAX
            response_left = self.client_left.read_holding_registers(address=7104, count=2)
            response_right = self.client_right.read_holding_registers(address=7104, count=2)
            self.write_to_file(registers_file, title="ANALOG POS MAX:", left_vals=[response_left.registers[0], response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # VELOCITY 
            response_left = self.client_left.read_holding_registers(address=7106, count=2)
            response_right = self.client_right.read_holding_registers(address=7106, count=2)
            self.write_to_file(registers_file, title="VELOCITY:", left_vals=[response_left.registers[0], response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # ACCEL
            response_left = self.client_left.read_holding_registers(address=7108, count=2)
            response_right = self.client_right.read_holding_registers(address=7108, count=2)
            self.write_to_file(registers_file, title="ACCEL:", left_vals=[response_left.registers[0], response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # MODBUSCNTRL
            response_left = self.client_left.read_holding_registers(address=7188, count=1)
            response_right = self.client_right.read_holding_registers(address=7188, count=1)
            self.write_to_file(registers_file, title="MODBUSCNTRL:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # OEG status
            response_right = self.client_right.read_holding_registers(address=104, count=1)
            response_left = self.client_left.read_holding_registers(address=104, count=1)
            self.write_to_file(registers_file, title="OEG status:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # home position
            response_left = self.client_left.read_holding_registers(address=6002, count=2)
            response_right = self.client_right.read_holding_registers(address=6002, count=2)
            self.write_to_file(registers_file, title="home position:", left_vals=[response_left.registers[0], response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

        finally:
            registers_file.close()
                
    async def init(self):
        self.logger = setup_logging("read_telemetry", "read_telemetry.txt")
        self.wsclient = WebsocketClient(self.logger, on_message=self.on_message)
        self.BTfile = open("BoardTemp.txt", "w")
        self.ATfile = open("ActuatorTemp.txt", "w")
        self.ICfile = open("IContinous.txt", "w")
        self.VBUSfile = open("VBUS.txt", "w")
        await self.wsclient.connect()
        
    async def main(self):
        try:
            await self.init()
            elapsed_time = 0
            max_duration = 120
            start = time().time()
            while elapsed_time<=max_duration:
                self.wsclient.send("action=readtelemetry|")
                await asyncio.sleep(0.1)
                elapsed_time = time.time() - start
                
        except Exception as e:
            print(f"Error while reading registers: {e}")
        finally: 
            self.BTfile.close()
            self.ATfile.close()
            self.ICfile.close()
            self.VBUSfile.close()

if __name__ == "__main__":
    readValues = ReadValues()
    # asyncio.run(readValues.main())

    readValues.read_register()