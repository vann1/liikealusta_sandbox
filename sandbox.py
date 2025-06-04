from setup_logging import setup_logging
from pymodbus.client import ModbusTcpClient
from time import time
from websocket_client import WebsocketClient
import asyncio
import utils as utils
from motors_config import MotorConfig
from utils import extract_part
from test import bit_high_low
from IO_codes import OEG_MODE, IEG_MODE, IEG_MOTION

config = MotorConfig()

class Sandbox():
    SERVER_URL = "http://127.0.0.1:5001/"
    SERVER_IP_LEFT="192.168.0.211"
    SERVER_IP_RIGHT="192.168.0.212"
    SERVER_PORT=502
    client_left = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
    client_right = ModbusTcpClient(host=SERVER_IP_RIGHT, port=SERVER_PORT)
    logger = None
    wsclient = None
    
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

    def write_to_file(self, file, title, left_vals, right_vals, definitions=False):
        if not definitions:
            left_vals = ";".join([str(val) for val in left_vals])
            right_vals = ";".join([str(val) for val in right_vals])
            
        file.write(f"""
            #### - {title} - ####
            Left motor: {left_vals}
            Right motor: {right_vals}
            """)
    
    def get_active_bit_values(self, value, range_val=16):
        active_bit_values = []
        for n in range(range_val):
            if utils.is_nth_bit_on(n, value):
                active_bit_values.append(2**n)
                
        return active_bit_values

    def convert_bits_to_dict(self, value, dict="OEG_STATUS"):
        definitions = []
        if dict=="OEG_STATUS":
            acitive_values = self.get_active_bit_values(value)
            for value in acitive_values:
                definitions.append(OEG_MODE[value])
        elif dict=="IEG_MODE":
            acitive_values = self.get_active_bit_values(value)
            for value in acitive_values:
                definitions.append(IEG_MODE[value])
        elif dict=="IEG_MOTION":
            acitive_values = self.get_active_bit_values(value)
            for value in acitive_values:
                definitions.append(IEG_MOTION[value])

        return "\n".join(definitions)

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

            # HOST CURRENT MAX LIMIT - 9.7 
            response_left = self.client_left.read_holding_registers(address=6414, count=1)
            response_right = self.client_right.read_holding_registers(address=614, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 7)
            self.write_to_file(registers_file, title="HOST CURRENT MAX LIMIT - 9.7 :", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Factory LowVoltageTripLevel UVOLT16 - 11.5
            UVOLT16_DECIMAL_MAX = 2**5
            response_left = self.client_left.read_holding_registers(address=9200, count=1)
            response_right = self.client_right.read_holding_registers(address=9200, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 5)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 5)
            decimal_normalized_left = response_left_low / UVOLT16_DECIMAL_MAX
            decimal_normalized_right = response_right_low / UVOLT16_DECIMAL_MAX
            self.write_to_file(registers_file, title="LowVoltageTripLevel:", left_vals=[response_left_high, decimal_normalized_right], right_vals=[response_right_high, decimal_normalized_right])

            # Factory HighVoltageTripLevel UVOLT16 - 11.5
            response_left = self.client_left.read_holding_registers(address=9201, count=1)
            response_right = self.client_right.read_holding_registers(address=9201, count=1)
            response_left_high, response_left_low = bit_high_low(response_left.registers[0], 5)
            response_right_high, response_right_low = bit_high_low(response_right.registers[0], 5)
            decimal_normalized_left = response_left_low / UVOLT16_DECIMAL_MAX
            decimal_normalized_right = response_right_low / UVOLT16_DECIMAL_MAX

            self.write_to_file(registers_file, title="HighVoltageTripLevel:", left_vals=[response_left_high, decimal_normalized_left], right_vals=[response_right_high, decimal_normalized_right])

            # MAX CURRENT SINCE STARTUP
            response_left = self.client_left.read_holding_registers(address=576, count=2)
            response_right = self.client_right.read_holding_registers(address=576, count=2)
            response_left_high, response_left_low = bit_high_low(response_left.registers[1], 7)
            response_right_high, response_right_low = bit_high_low(response_right.registers[1], 7)
            self.write_to_file(registers_file, title="HOST CURRENT MAX LIMIT - 9.7 :", left_vals=[response_left_high, response_left.registers[0]], right_vals=[response_right_high, response_right.registers[0]])

            # MAX VOLTAGE SINCE STARTUP
            left_VBUS = self.client_left.read_holding_registers(address=578, count=2)
            right_VBUS = self.client_right.read_holding_registers(address=578, count=2)

            left_VBUS = left_VBUS.registers
            right_VBUS = right_VBUS.registers

            ### Extract the high value part and deccimal part
            left_VBUS_high, left_VBUS_low = utils.bit_high_low_both(left_VBUS[1], 5)
            right_VBUS_high, right_VBUS_low = utils.bit_high_low_both(right_VBUS[1], 5)

            left_vbus_decimal_val = utils.combine_to_21bit(left_VBUS[0], left_VBUS_low)
            right_vbus_decimal_val = utils.combine_to_21bit(right_VBUS[0], right_VBUS_low)

            left_vbus_decimal_val = utils.normalize_decimal_uvolt32(left_vbus_decimal_val)
            right_vbus_decimal_val = utils.normalize_decimal_uvolt32(right_vbus_decimal_val)

            ### CONVERT VBUS HIGH INTO ACTUAL VALUE IT USES TWO's COMPLEMENT
            left_VBUS_high = utils.get_twos_complement(10, left_VBUS_high)
            right_VBUS_high = utils.get_twos_complement(10, right_VBUS_high)

            left_VBUS = left_VBUS_high + left_vbus_decimal_val
            right_VBUS = right_VBUS_high + right_vbus_decimal_val
            self.write_to_file(registers_file, title="MAX VOLTAGE SINCE STARTUP", left_vals=[left_VBUS], right_vals=[right_VBUS])

            # HOME PRIMARY OPTIONS FLAG MAP - infinite negative
            response_left = self.client_left.read_holding_registers(address=6414, count=1)
            response_right = self.client_right.read_holding_registers(address=614, count=1)
            self.write_to_file(registers_file, title="HOME PRIMARY OPTIONS FLAG MAP -:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

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
            left_definitons = self.convert_bits_to_dict(response_left.registers[0])
            right_definitions = self.convert_bits_to_dict(response_right.registers[0])
            self.write_to_file(registers_file, title="OEG status:", left_vals=left_definitons, right_vals=right_definitions, definitions=True)

            # home position
            response_left = self.client_left.read_holding_registers(address=6002, count=2)
            response_right = self.client_right.read_holding_registers(address=6002, count=2)
            self.write_to_file(registers_file, title="home position:", left_vals=[response_left.registers[0], response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])
             
            # Fault disables
            response_left = self.client_left.read_holding_registers(address=5102, count=1)
            response_right = self.client_right.read_holding_registers(address=5102, count=1)
            self.write_to_file(registers_file, title="FaultDisables: ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])
             
            # Fault stop
            response_left = self.client_left.read_holding_registers(address=5104, count=1)
            response_right = self.client_right.read_holding_registers(address=5104, count=1)
            self.write_to_file(registers_file, title="FaultStop: ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 1 ID
            response_left = self.client_left.read_holding_registers(address=4100, count=1)
            response_right = self.client_right.read_holding_registers(address=4100, count=1)
            self.write_to_file(registers_file, title="-- SCOPE CONTROL REGISTERS -- \n Channel 1 ID ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 1 Flags
            response_left = self.client_left.read_holding_registers(address=4101, count=1)
            response_right = self.client_right.read_holding_registers(address=4101, count=1)
            self.write_to_file(registers_file, title="Channel 1 Flags ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 2 ID
            response_left = self.client_left.read_holding_registers(address=4102, count=1)
            response_right = self.client_right.read_holding_registers(address=4102, count=1)
            self.write_to_file(registers_file, title="Channel 2 ID ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 2 Flags
            response_left = self.client_left.read_holding_registers(address=4103, count=1)
            response_right = self.client_right.read_holding_registers(address=4103, count=1)
            self.write_to_file(registers_file, title="Channel 2 Flags ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 3 ID
            response_left = self.client_left.read_holding_registers(address=4104, count=1)
            response_right = self.client_right.read_holding_registers(address=4104, count=1)
            self.write_to_file(registers_file, title="Channel 3 ID ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 3 Flags
            response_left = self.client_left.read_holding_registers(address=4105, count=1)
            response_right = self.client_right.read_holding_registers(address=4105, count=1)
            self.write_to_file(registers_file, title="Channel 3 Flags ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 4 ID
            response_left = self.client_left.read_holding_registers(address=4106, count=1)
            response_right = self.client_right.read_holding_registers(address=4106, count=1)
            self.write_to_file(registers_file, title="Channel 4 ID ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Channel 4 Flags
            response_left = self.client_left.read_holding_registers(address=4107, count=1)
            response_right = self.client_right.read_holding_registers(address=4107, count=1)
            self.write_to_file(registers_file, title="Channel 4 Flags ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Trigger ID
            response_left = self.client_left.read_holding_registers(address=4108, count=1)
            response_right = self.client_right.read_holding_registers(address=4108, count=1)
            self.write_to_file(registers_file, title="Trigger ID ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Trigger Flags
            response_left = self.client_left.read_holding_registers(address=4109, count=1)
            response_right = self.client_right.read_holding_registers(address=4109, count=1)
            self.write_to_file(registers_file, title="Trigger Flags ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Trigger Level
            response_left = self.client_left.read_holding_registers(address=4110, count=2)
            response_right = self.client_right.read_holding_registers(address=4110, count=2)
            self.write_to_file(registers_file, title="Trigger Level ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # Pretrigger Trigger
            response_left = self.client_left.read_holding_registers(address=4112, count=2)
            response_right = self.client_right.read_holding_registers(address=4112, count=2)
            self.write_to_file(registers_file, title="Pretrigger Trigger ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # Update Rate
            response_left = self.client_left.read_holding_registers(address=4114, count=1)
            response_right = self.client_right.read_holding_registers(address=4114, count=1)
            self.write_to_file(registers_file, title="Update rate ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Control
            response_left = self.client_left.read_holding_registers(address=4115, count=1)
            response_right = self.client_right.read_holding_registers(address=4115, count=1)
            self.write_to_file(registers_file, title="Control ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # SCOPE STATUS REGISTERS
            ### Status
            response_left = self.client_left.read_holding_registers(address=400, count=1)
            response_right = self.client_right.read_holding_registers(address=400, count=1)
            self.write_to_file(registers_file, title="-- SCOPE STATUS REGISTERS -- \n Status ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])            

            ### Status
            response_left = self.client_left.read_holding_registers(address=401, count=1)
            response_right = self.client_right.read_holding_registers(address=401, count=1)
            self.write_to_file(registers_file, title="-- Record Count ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])            

            ### Max Records
            response_left = self.client_left.read_holding_registers(address=402, count=1)
            response_right = self.client_right.read_holding_registers(address=402, count=1)
            self.write_to_file(registers_file, title="-- Max Records ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])  

            ### Record Size
            response_left = self.client_left.read_holding_registers(address=403, count=1)
            response_right = self.client_right.read_holding_registers(address=403, count=1)
            self.write_to_file(registers_file, title="-- Record Size ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])  

            ### Buffer Size
            response_left = self.client_left.read_holding_registers(address=404, count=1)
            response_right = self.client_right.read_holding_registers(address=404, count=1)
            self.write_to_file(registers_file, title="-- Buffer Size ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])  

            ### Timestamp
            response_left = self.client_left.read_holding_registers(address=405, count=1)
            response_right = self.client_right.read_holding_registers(address=405, count=1)
            self.write_to_file(registers_file, title="-- Time Stamp ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])  

            # Channel1
            response_left = self.client_left.read_holding_registers(address=406, count=2)
            response_right = self.client_right.read_holding_registers(address=406, count=2)
            self.write_to_file(registers_file, title="Recent channel 1 value ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # Channel 2
            response_left = self.client_left.read_holding_registers(address=408, count=2)
            response_right = self.client_right.read_holding_registers(address=408, count=2)
            self.write_to_file(registers_file, title="Recent channel 2 value ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # Channel 3
            response_left = self.client_left.read_holding_registers(address=410, count=2)
            response_right = self.client_right.read_holding_registers(address=410, count=2)
            self.write_to_file(registers_file, title="Recent channel 3 value ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # Channel 4
            response_left = self.client_left.read_holding_registers(address=412, count=2)
            response_right = self.client_right.read_holding_registers(address=412, count=2)
            self.write_to_file(registers_file, title="Recent channel 4 value ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])

            # Current Trigger value
            response_left = self.client_left.read_holding_registers(address=414, count=2)
            response_right = self.client_right.read_holding_registers(address=414, count=2)
            self.write_to_file(registers_file, title="Current Trigger value ", left_vals=[response_left.registers[0],response_left.registers[1]], right_vals=[response_right.registers[0], response_right.registers[1]])
        finally:
            registers_file.close()

    def reset_ieg_mode(self):
        self.client_left.write_register(address=config.IEG_MODE, value=0)
        self.client_right.write_register(address=config.IEG_MODE, value=0)
              
    async def init(self):
        self.client_right.connect()
        self.client_left.connect()
        self.logger = setup_logging("read_telemetry", "read_telemetry.txt")
        self.wsclient = WebsocketClient(self.logger, on_message=self.on_message)
        self.BTfile = open("BoardTemp.txt", "w")
        self.ATfile = open("ActuatorTemp.txt", "w")
        self.ICfile = open("IContinous.txt", "w")
        self.VBUSfile = open("VBUS.txt", "w")
        await self.wsclient.connect()
            
    def registers_convertion(self, register,format,signed=False):
        format_1, format_2 = format.split(".")
        format_1 = int(format_1)
        format_2 = int(format_2)
        
        if len(register) == 1: # Single register Example 9.7
                # Seperates single register by format
                register_high, register_low = utils.bit_high_low_both(register[0], format_2)
                # Normalizes decimal between 0-1
                register_low_normalized = utils.general_normalize_decimal(register_low, format_2)
                # If signed checks whether if its two complement
                if signed: 
                    register_high = utils.get_twos_complement(format_1 - 1, register_high)

                return register_high + register_low_normalized
        else: # Two registers
            # Checks what's the format. Examples: 16.16, 8.24, 12.20
            if format_1 <= 16 and format_2 >= 16: 
                # Format difference for seperating "shared" register
                format_difference = 16 - format_1 
                # Seperates "shared" register
                register_val_high, register_val_low = utils.bit_high_low_both(register[1], format_difference)
                # Combines decimal values into a single binary
                register_val_low = utils.combine_bits(register_val_low,register[0])
                # Normalizes decimal between 0-1
                register_low_normalized = utils.general_normalize_decimal(register_val_low, format_2)
                # If signed checks whether if its two complement
                if signed: 
                    register_val_high = utils.get_twos_complement(format_1 - 1, register_val_high)
                
                return register_val_high + register_low_normalized

            else: # Examples: 32.0 20.12 30.2
                # Format difference for seperating "shared" register
                format_difference = 32 - format_1
                # Seperates "shared" register
                register_val_high, register_val_low = utils.bit_high_low_both(register[0], format_difference)
                # Combines integer values into a single binary
                register_val_high = utils.combine_bits(register[1],register_val_high)
                # Normalizes decimal between 0-1
                register_low_normalized = utils.general_normalize_decimal(register_val_low, format_2)
                # If signed checks whether if its two complement
                if signed:
                    register_val_high = utils.get_twos_complement(format_1 - 1, register_val_high)
                return register_val_high + register_low_normalized
              
    async def main(self):
        try:
            await self.init()
            elapsed_time = 0
            max_duration = 120
            start = time()
            while elapsed_time<=max_duration:
                await self.wsclient.send("action=readtelemetry|")
                await asyncio.sleep(0.1)
                elapsed_time = time() - start
        except KeyboardInterrupt:  
                pass
        except Exception as e:
            print(f"Error while reading registers: {e}")
        finally: 
            await self.wsclient.close()
            self.BTfile.close()
            self.ATfile.close()
            self.ICfile.close()
            self.VBUSfile.close()

if __name__ == "__main__":
    readValues = Sandbox()
    # asyncio.run(readValues.main())

    # readValues.read_register()
    # readValues.reset_ieg_mode()