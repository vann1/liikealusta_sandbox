from setup_logging import setup_logging
from pymodbus.client import ModbusTcpClient
from time import time,sleep
from websocket_client import WebSocketClient
import asyncio
import utils as utils
from motors_config import MotorConfig
from utils import extract_part, is_nth_bit_on
from test import bit_high_low
from IO_codes import OEG_MODE, IEG_MODE, IEG_MOTION, FAULTS, OPTIONS
from tcp_socket_client import TCPSocketClient
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
    telemetry_data_ready=False
    
    def in_position(self, n=20) -> bool:
        """Polls for n amount of time to check 
        if the motors are in position or not"""
        max_polling_duration=n
        elapsed_time = 0
        start_time = time()
        while max_polling_duration >= elapsed_time:
            lr = self.client_left.read_holding_registers(address=105, count=1).registers[0]
            rr = self.client_right.read_holding_registers(address=105, count=1).registers[0]
            if is_nth_bit_on(12, lr) and is_nth_bit_on(12, rr):
                return True
            elapsed_time = time() - start_time
        
        self.logger.error("Motors failed to be in position in the given time limit")
        return False


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
        elif dict=="FAULT":
            acitive_values = self.get_active_bit_values(value)
            for value in acitive_values:
                definitions.append(FAULTS[value])
        elif dict=="OPTIONS":
            acitive_values = self.get_active_bit_values(value)
            for value in acitive_values:
                definitions.append(OPTIONS[value])

        return "\n".join(definitions)

    def read_register(self):
        try:
            registers_file = open("registers.txt", "w")
            # RECENTFAULT #1
            response_left = self.client_left.read_holding_registers(address=846, count=1)
            response_right = self.client_right.read_holding_registers(address=846, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0], "FAULT")
            right_definitions = self.convert_bits_to_dict(response_right.registers[0], "FAULT")
            self.write_to_file(file=registers_file, title="Recent fault #1 ", left_vals=[left_definitons], right_vals=[right_definitions])
            # RECENTFAULT #1 PowerupCount
            response_left = self.client_left.read_holding_registers(address=847, count=1)
            response_right = self.client_right.read_holding_registers(address=847, count=1)
            self.write_to_file(file=registers_file, title="Recent fault #1 UC", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])
            # DISABLING FAULTS
            response_left = self.client_left.read_holding_registers(address=5102, count=1)
            response_right = self.client_right.read_holding_registers(address=5102, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0], "FAULT")
            right_definitions = self.convert_bits_to_dict(response_right.registers[0], "FAULT")
            self.write_to_file(file=registers_file, title="ALL DISABLING FAULTS ", left_vals=[left_definitons], right_vals=[right_definitions])

            # DRIVE OPTIONS
            response_left = self.client_left.read_holding_registers(address=5100, count=1)
            response_right = self.client_right.read_holding_registers(address=5100, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0], "OPTIONS")
            right_definitions = self.convert_bits_to_dict(response_right.registers[0], "OPTIONS")
            self.write_to_file(file=registers_file, title="DRIVE OPTIONS ", left_vals=[left_definitons], right_vals=[right_definitions])

            # Plimit minus
            response_left = self.client_left.read_holding_registers(address=5118, count=2)
            response_right = self.client_right.read_holding_registers(address=5118, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)
            self.write_to_file(file=registers_file, title="Plimit minus", left_vals=[response_left], right_vals=[response_right])

            # Plimit plus
            response_left = self.client_left.read_holding_registers(address=5120, count=2)
            response_right = self.client_right.read_holding_registers(address=5120, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)
            self.write_to_file(file=registers_file, title="Plimit plus", left_vals=[response_left], right_vals=[response_right])

            # plimit velocity
            response_left = self.client_left.read_holding_registers(address=5124, count=2)
            response_right = self.client_right.read_holding_registers(address=5124, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="8.24", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="8.24", signed=False)
            self.write_to_file(file=registers_file, title="plimit velocity", left_vals=[response_left], right_vals=[response_right])

            # Plimit foldback
            response_left = self.client_left.read_holding_registers(address=5126, count=1)
            response_right = self.client_right.read_holding_registers(address=5126, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)
            self.write_to_file(file=registers_file, title="Plimit foldback", left_vals=[response_left], right_vals=[response_right])

            # Plimit ipeak
            response_left = self.client_left.read_holding_registers(address=5127, count=1)
            response_right = self.client_right.read_holding_registers(address=5127, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)
            self.write_to_file(file=registers_file, title="# Plimit ipeak", left_vals=[response_left], right_vals=[response_right])

            # Ipeak time
            response_left = self.client_left.read_holding_registers(address=5128, count=1)
            response_right = self.client_right.read_holding_registers(address=5128, count=1)
            response_left = response_left.registers[0] * 0.001        
            response_right = response_right.registers[0] * 0.001
            self.write_to_file(file=registers_file, title="Ipeak time", left_vals=[response_left], right_vals=[response_right])

            ### ALL PRESENT FAULTS
            response_left = self.client_left.read_holding_registers(address=5, count=1)
            response_right = self.client_right.read_holding_registers(address=5, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0], "FAULT")
            right_definitions = self.convert_bits_to_dict(response_right.registers[0], "FAULT")
            self.write_to_file(file=registers_file, title="ALL PRESENT FAULTS ", left_vals=[left_definitons], right_vals=[right_definitions])

             ### ALL DISABLING FAULTS
            response_left = self.client_left.read_holding_registers(address=6, count=1)
            response_right = self.client_right.read_holding_registers(address=6, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0], "FAULT")
            right_definitions = self.convert_bits_to_dict(response_right.registers[0], "FAULT")
            self.write_to_file(file=registers_file, title="ALL DISABLING FAULTS", left_vals=[left_definitons], right_vals=[right_definitions])

            ### ALL SOFT FAULTS
            response_left = self.client_left.read_holding_registers(address=7, count=1)
            response_right = self.client_right.read_holding_registers(address=7, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0], "FAULT")
            right_definitions = self.convert_bits_to_dict(response_right.registers[0], "FAULT")
            self.write_to_file(file=registers_file, title="ALL SOFT FAULTS", left_vals=[left_definitons], right_vals=[right_definitions])

            ### prEsent current
            response_left = self.client_left.read_holding_registers(address=566, count=2)
            response_right = self.client_right.read_holding_registers(address=566, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="9.23", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.23", signed=False)
            self.write_to_file(file=registers_file, title="preEsent current ", left_vals=[response_left], right_vals=[response_right])

            # OEG status
            response_right = self.client_right.read_holding_registers(address=104, count=1)
            response_left = self.client_left.read_holding_registers(address=104, count=1)
            left_definitons = self.convert_bits_to_dict(response_left.registers[0])
            right_definitions = self.convert_bits_to_dict(response_right.registers[0])
            self.write_to_file(registers_file, title="OEG status:", left_vals=left_definitons, right_vals=right_definitions, definitions=True)
            ### Host position
            response_left = self.client_left.read_holding_registers(address=4304, count=2)
            response_right = self.client_right.read_holding_registers(address=4304, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)  
            self.write_to_file(file=registers_file, title="Host position commanded position ", left_vals=[response_left], right_vals=[response_right])

            ### pfeedback position
            response_left = self.client_left.read_holding_registers(address=378, count=2)
            response_right = self.client_right.read_holding_registers(address=378, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)  
            self.write_to_file(file=registers_file, title="current pfeedback position", left_vals=[response_left], right_vals=[response_right])

            ### Current position
            response_left = self.client_left.read_holding_registers(address=4304, count=2)
            response_right = self.client_right.read_holding_registers(address=4304, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)  
            self.write_to_file(file=registers_file, title="Host position commanded position ", left_vals=[response_left], right_vals=[response_right])

            # Factory BoardTempTripLevel BTMP16 - 11.5
            response_left = self.client_left.read_holding_registers(address=9202, count=1)
            response_right = self.client_right.read_holding_registers(address=9202, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="11.5", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="11.5", signed=False)  
            self.write_to_file(file=registers_file, title="Factory BoardTempTripLevel BTMP16 ", left_vals=[response_left], right_vals=[response_right])

            # Factory IPEAK UCUR16
            response_left = self.client_left.read_holding_registers(address=9204, count=1)
            response_right = self.client_right.read_holding_registers(address=9204, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)  
            self.write_to_file(registers_file, title="Factory IPEAK UCUR16 ", left_vals=[response_left], right_vals=[response_right])

            # Factory Icontinious UCUR16
            response_left = self.client_left.read_holding_registers(address=9205, count=1)
            response_right = self.client_right.read_holding_registers(address=9205, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)  
            self.write_to_file(registers_file, title="Factory Icontinious UCUR16 ", left_vals=[response_left], right_vals=[response_right])
            
            # Factory ActuatorTempTripLevel ATMP16 - 13.3
            response_left = self.client_left.read_holding_registers(address=9209, count=1)
            response_right = self.client_right.read_holding_registers(address=9209, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="13.3", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="13.3", signed=False)  
            self.write_to_file(registers_file, title="Factory ActuatorTempTripLevel ATMP16 ", left_vals=[response_left], right_vals=[response_right])

            # Factory LowVoltageTripLevel UVOLT16 - 11.5
            response_left = self.client_left.read_holding_registers(address=9200, count=1)
            response_right = self.client_right.read_holding_registers(address=9200, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="11.5", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="11.5", signed=False)  
            self.write_to_file(registers_file, title="LowVoltageTripLevel ", left_vals=[response_left], right_vals=[response_right])

            # Factory HighVoltageTripLevel UVOLT16 - 11.5
            response_left = self.client_left.read_holding_registers(address=9201, count=1)
            response_right = self.client_right.read_holding_registers(address=9201, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="11.5", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="11.5", signed=False)  
            self.write_to_file(registers_file, title="HighVoltageTripLevel ", left_vals=[response_left], right_vals=[response_right])

            # MAX CURRENT SINCE STARTUP UCUR32
            response_left = self.client_left.read_holding_registers(address=576, count=2)
            response_right = self.client_right.read_holding_registers(address=576, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="9.23", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.23", signed=False)  
            self.write_to_file(registers_file, title="Max current observed ", left_vals=[response_left], right_vals=[response_right])

            # MAX VOLTAGE SINCE STARTUP 11.21
            response_left = self.client_left.read_holding_registers(address=578, count=2)
            response_right = self.client_right.read_holding_registers(address=578, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="11.21", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="11.21", signed=False)  
            self.write_to_file(registers_file, title="MAX VOLTAGE SINCE STARTUP ",  left_vals=[response_left], right_vals=[response_right])

            # HOME PRIMARY OPTIONS FLAG MAP - infinite negative
            response_left = self.client_left.read_holding_registers(address=6414, count=1)
            response_right = self.client_right.read_holding_registers(address=6414, count=1)
            self.write_to_file(registers_file, title="HOME PRIMARY OPTIONS FLAG MAP -:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # User defined IPEAK - 2560 UCUR16
            response_left = self.client_left.read_holding_registers(address=5108, count=1)
            response_right = self.client_right.read_holding_registers(address=5108, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)  
            self.write_to_file(registers_file, title="User defined IPEAK - 2560:", left_vals=[response_left], right_vals=[response_right])

            # Current operation mode
            response_left = self.client_left.read_holding_registers(address=31, count=1)
            response_right = self.client_right.read_holding_registers(address=31, count=1)
            self.write_to_file(registers_file, title="Current operation mode:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # current revolutions
            response_left = self.client_left.read_holding_registers(address=378, count=2)
            response_right = self.client_right.read_holding_registers(address=378, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=True)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=True)  
            self.write_to_file(registers_file, title="current revolutions:", left_vals=[response_left], right_vals=[response_right])

            # host control command mode
            response_left = self.client_left.read_holding_registers(address=4303, count=1)
            response_right = self.client_right.read_holding_registers(address=4303, count=1)
            self.write_to_file(registers_file, title="host control command mode:", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

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
            response_left = utils.registers_convertion(response_left.registers, format="16.0", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.0", signed=False)
            self.write_to_file(registers_file, title="IEG MODE:", left_vals=[response_left], right_vals=[response_right])

            # IEG MOTION
            response_left = self.client_left.read_holding_registers(address=4317, count=1)
            response_right = self.client_right.read_holding_registers(address=4317, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="16.0", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.0", signed=False)
            self.write_to_file(registers_file, title="IEG MOTION:", left_vals=[response_left], right_vals=[response_right])

            # home position
            response_left = self.client_left.read_holding_registers(address=6002, count=2)
            response_right = self.client_right.read_holding_registers(address=6002, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=True)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=True)
            self.write_to_file(registers_file, title="home position:", left_vals=[response_left], right_vals=[response_right])
             
             
            # Fault stop
            response_left = self.client_left.read_holding_registers(address=5104, count=1)
            response_right = self.client_right.read_holding_registers(address=5104, count=1)
            self.write_to_file(registers_file, title="FaultStop: ", left_vals=[response_left.registers[0]], right_vals=[response_right.registers[0]])

            # Host current UCUR16 9.7 4310
            response_left = self.client_left.read_holding_registers(address=4310, count=1)
            response_right = self.client_right.read_holding_registers(address=4310, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)  
            
            self.write_to_file(registers_file, title="Host Current ", left_vals=[response_left], right_vals=[response_right])
            # Ilimitminus 40 9.23 SIGNED
            response_left = self.client_left.read_holding_registers(address=40, count=2)
            response_right = self.client_right.read_holding_registers(address=40, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="9.23", signed=True)        
            response_right = utils.registers_convertion(response_right.registers, format="9.23", signed=True)  
            self.write_to_file(registers_file, title="Ilimitminus ", left_vals=[response_left], right_vals=[response_right])
            
            # Ilimitsplus 42 9.23 SIGNED
            response_left = self.client_left.read_holding_registers(address=42, count=2)
            response_right = self.client_right.read_holding_registers(address=42, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="9.23", signed=True)        
            response_right = utils.registers_convertion(response_right.registers, format="9.23", signed=True)  
            self.write_to_file(registers_file, title="Ilimitsplus ", left_vals=[response_left], right_vals=[response_right])
            
            # PErrorMin
            response_left = self.client_left.read_holding_registers(address=384, count=2)
            response_right = self.client_right.read_holding_registers(address=384, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=True)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=True)  
            self.write_to_file(registers_file, title="PErrorMin ", left_vals=[response_left], right_vals=[response_right])
        
            # PErrorMax
            response_left = self.client_left.read_holding_registers(address=386, count=2)
            response_right = self.client_right.read_holding_registers(address=386, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=True)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=True)  
            self.write_to_file(registers_file, title="PErrorMax ", left_vals=[response_left], right_vals=[response_right])
            
            # MaxFollowingError 5114 
            response_left = self.client_left.read_holding_registers(address=5114, count=2)
            response_right = self.client_right.read_holding_registers(address=5114, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)  
            self.write_to_file(registers_file, title="MaxFollowingError ", left_vals=[response_left], right_vals=[response_right])
            
            # MaxFollowingErrorTime 5117 
            response_left = self.client_left.read_holding_registers(address=5117, count=1)
            response_right = self.client_right.read_holding_registers(address=5117, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="16.0", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.0", signed=False)  
            self.write_to_file(registers_file, title="MaxFollowingErrorTime ", left_vals=[response_left], right_vals=[response_right])
            
            # ITrip 9203 
            response_left = self.client_left.read_holding_registers(address=9203, count=1)
            response_right = self.client_right.read_holding_registers(address=9203, count=1)
            response_left = utils.registers_convertion(response_left.registers, format="9.7", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="9.7", signed=False)  
            self.write_to_file(registers_file, title="ITrip ", left_vals=[response_left], right_vals=[response_right])
        finally:
            registers_file.close()

    async def make_sample_rotations(self):
        n = 10
        step_change = 17/(n-1)
        max_pitch = 8.5
        for i in range(n):
            await self.wsclient.send(f"action=rotate|pitch={max_pitch-(i*step_change)}|roll={0}|")
            wut = max_pitch-(i*step_change)
            print(f"wut {wut} i {i}")
            await asyncio.sleep(0.5)
            if self.in_position():
                self.iMU_client.send_message("action=r_xl|")
                if self.is_data_ready():
                    r_left_revs, r_right_revs = self.get_current_position()
                    self.telemetry_data_ready = False
                    self.dataset.write(f"{self.pitch},{self.roll},{r_left_revs},{r_right_revs}\n")
        self.dataset.close()
        
    def get_current_position(self):
        try:
            response_left = self.client_left.read_holding_registers(address=378, count=2)
            response_right = self.client_right.read_holding_registers(address=378, count=2)
            response_left = utils.registers_convertion(response_left.registers, format="16.16", signed=False)        
            response_right = utils.registers_convertion(response_right.registers, format="16.16", signed=False)
            return (response_left,response_right)
        except:
            return ("N/A","N/A")
    
    def is_data_ready(self, n=20) -> bool:
        """Polls for n amount of time to check 
        if the telemetry data have been recevied"""
        max_polling_duration=n
        elapsed_time = 0
        start_time = time()
        while max_polling_duration >= elapsed_time:
            if self.telemetry_data_ready:  
                return True
            else:
                sleep(0.1)
            elapsed_time = time() - start_time
        self.logger.error("Motors failed to be in position in the given time limit")
        return False
    def set_disabling_fault(self):
        self.client_left.write_register(address=5102, value=59903+1024)
        self.client_right.write_register(address=5102, value=59903+1024)    

    def reset_ieg_mode(self):
        self.client_left.write_register(address=config.IEG_MODE, value=0)
        self.client_right.write_register(address=config.IEG_MODE, value=0)
    def recive_telemetry_data(self,message):
        message=extract_part("message=", message)
        pitch,roll = message.split(",")
        pitch = float(pitch)
        roll = float(roll)
        roll -= 0.6
        print(pitch,",",roll) 
        self.pitch = pitch
        self.roll = roll
        self.telemetry_data_ready = True     

    async def init(self, files=True):
        try:
            self.iMU_client = TCPSocketClient(host="10.214.33.19", port=7001, on_message_received=self.recive_telemetry_data)
            self.iMU_client.connect()
            self.client_right.connect()
            self.client_left.connect()
            self.logger = setup_logging("read_telemetry", "read_telemetry.txt")
            self.dataset = open("Angle_dataset.csv", "a")
            self.wsclient = WebSocketClient(self.logger, on_message=self.on_message, on_message_async=True, identity="sandbox")
            if files:
                self.BTfile = open("BoardTemp.txt", "w")
                self.ATfile = open("ActuatorTemp.txt", "w")
                self.ICfile = open("IContinous.txt", "w")
                self.VBUSfile = open("VBUS.txt", "w")
            await self.wsclient.connect()
        except Exception as e:
            self.logger.error("TÄSSÄ",e)
    
    async def asd(self):
        try:
            await self.init(files=False)
            
            await self.make_sample_rotations()
        except Exception as e:
            print(e)
        finally:
            await self.wsclient.close()


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
            
    def faultreset(self):
        """Clears all active faults from both actuators."""
        self.client_left.write_register(address=4316,value=32768)
        self.client_left.write_register(address=4316,value=32768)


if __name__ == "__main__":
    sandbox = Sandbox()
    asyncio.run(sandbox.asd())
    # asyncio.run(readValues.main())
    # sandbox.faultreset()
    # readValues.reset_ieg_mode()
    # sandbox.read_register()
