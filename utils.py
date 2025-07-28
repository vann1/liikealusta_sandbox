import math
import logging
from pathlib import Path

FAULT_RESET_BIT = 15
ENABLE_MAINTAINED_BIT = 1
ALTERNATE_MODE_BIT = 7
CONTINIOUS_CURRENT_BIT = 1
BOARD_TEMPERATURE_BIT = 7
ACTUATOR_TEMPERATURE = 8

UVEL32_RESOLUTION = 1 / (2**24)
UACC32_RESOLUTION = 1 / (2**20)
UCUR16_RESOLUTION = 1 / (2**7)

UCUR16_LOW_MAX = 2**7
UCUR32_DECIMAL_MAX = 2**23
UVOLT32_DECIMAL_MAX = 2**21

def convert_val_into_twoscomplenent(target_value, n) -> int:
       """ Expects the target value to be expressed as negative
       if desired to have it in twos complement form """
       if target_value < 0:
        highest_bit = 2**n
        target = target_value+highest_bit
        return target
       else:
              return target_value

def convert_val_into_format(value, format, signed=False):
    """
    Takes in a desired value and register format as
      a param and returns it in the correct form
    """
    formats = format.split(".")
    register_size = 16
    if len(formats) < 2:
        raise ValueError()

    try:
        format1 = abs(int(formats[0]))
        format2 = abs(int(formats[1]))
    except ValueError:
        raise
    
    decimal, whole = math.modf(value) 
    n = format1-1
    whole = int(whole)
    
    ### 1 register
    if format1 <= 16 and format2 <= 16 and format1+format2 == 16:
        if format2 == 0:
            return whole
            
        low_val = unnormalize_decimal(decimal, format2)
        whole_val = whole << format2
        if signed:
               whole = convert_val_into_twoscomplenent(target_value=whole, n=n)

        result = whole_val | low_val
        return result
    ### 2 registers
    elif format1 <= 16 and format2 >= 16 and format1+format2 == 32:
        low_val = unnormalize_decimal(decimal=decimal, max_n=format2)
        format_diff = format2 - register_size 
        whole_val = whole << format_diff
        if signed:
                whole = convert_val_into_twoscomplenent(target_value=whole, n=n)
        high_decimal_part = format2 - register_size
        low_dec_val, high_dec_val = split_nbit_to_decimal_components(value=low_val, high_decimal_part=high_decimal_part)

        return [low_dec_val, whole_val | high_dec_val]
    else:
        raise Exception("Unsupported format")

def format_response(**kwargs):
       """
       Expects possible kwargs of event=event, action=action, message=message
       """
       msg_parts = []
       for key, val in kwargs.items():
              msg_parts.append(f"|{key}={val}|")
        
       return "".join(msg_parts)

result  = format_response(action="stop")
print(f"RESULT : {result}" )

def registers_convertion(registers,format,signed=False, scale=1):
        formats = format.split(".")
        
        if len(formats) < 2:
                raise(ValueError)
        
        format_1, format_2 = formats
        try:
                format_1 = int(format_1)
                format_2 = int(format_2)
        except ValueError:
                raise
        format1_n = format_1-1
        register_size = 16
        if len(registers) == 1 and format_1 + format_2 == 16: # Single register Example 9.7
                # Seperates single register by format
                register_high, register_low = bit_high_low_both(registers[0], format_2)
                # Normalizes decimal between 0-1
                register_low_normalized = general_normalize_decimal(register_low, format_2)
                # If signed checks whether if its two complement
                if signed: 
                        register_high = get_twos_complement(format_1 - 1, register_high)
                return (register_high + register_low_normalized) * scale
        else: # Two registers
                # Checks what's the format. Examples: 16.16, 8.24, 12.20
                decimal_lower_register = registers[0]
                shared_register = registers[1]
                if format_1 <= 16 and format_2 >= 16 and format_1 + format_2 == 32: 
                        # Format difference for seperating "shared" register
                        upper_decimal_format = register_size - format_1 
                        # Seperates "shared" register
                        integer_part, decimal_higher_bits = bit_high_low_both(shared_register, upper_decimal_format)
                        # Combines decimal values into a single binary
                        decimal_combined = combine_bits(decimal_higher_bits,decimal_lower_register)
                        # Normalizes decimal between 0-1
                        register_low_normalized = general_normalize_decimal(decimal_combined, format_2)
                        # If signed checks whether if its two complement
                        if signed: 
                                integer_part = get_twos_complement(format1_n, integer_part)
                        return (integer_part + register_low_normalized) * scale
                else: # Examples: 32.0 20.12 30.2
                        # Format difference for seperating "shared" register
                        decimal_format = 32 - format_1
                        # Seperates "shared" register
                        register_val_high, register_val_low = bit_high_low_both(registers[0], decimal_format)
                        # Combines integer values into a single binary
                        register_val_high = combine_bits(registers[1],register_val_high)
                        # Normalizes decimal between 0-1
                        register_low_normalized = general_normalize_decimal(register_val_low, format_2)
                        # If signed checks whether if its two complement
                        if signed:
                                register_val_high = get_twos_complement(format1_n, register_val_high)
                        return (register_val_high + register_low_normalized) * scale

def combine_bits(high_bit_part, low_bit_part):
        return (high_bit_part << 16) | low_bit_part

def general_normalize_decimal(value, max_n):
        return value / 2**max_n

def unnormalize_decimal(decimal, max_n):
        return abs(int(decimal * 2**max_n))

def convert_to_revs(pfeedback):
    decimal = pfeedback[0] / 65536
    num = pfeedback[1]
    return num + decimal

def extract_part(part, message):
    start_idx = message.find(part)
    if start_idx == -1:
        return False
    
    start_idx += len(part)
    pipe_idx = message.find("|", start_idx)
    if pipe_idx == -1:
        return False
    
    return  message[start_idx:pipe_idx]

def is_nth_bit_on(n, number):
            mask = 1 << n
            return (number & mask) != 0

# Only allows the needed bits
def IEG_MODE_bitmask_default(number):
        mask = (1 << FAULT_RESET_BIT) | (1 << ENABLE_MAINTAINED_BIT)
        number = number & 0xFFFF
        return number & mask

# Only allows the needed bits
def is_fault_critical(number):
        mask = (1 << CONTINIOUS_CURRENT_BIT) | (1 << BOARD_TEMPERATURE_BIT) | (1 << ACTUATOR_TEMPERATURE)
        number = number & 0xFFFF
        return (number & mask) != 0

def IEG_MODE_bitmask_alternative(number):
        mask = (1 << FAULT_RESET_BIT) | (1 << ALTERNATE_MODE_BIT) |(1 << ENABLE_MAINTAINED_BIT) 
        number = number & 0xFFFF
        return number & mask

def IEG_MODE_bitmask_enable(number):
        mask = (1 << ENABLE_MAINTAINED_BIT)
        number = number & 0xFFFF
        return number & mask

def split_nbit_to_decimal_components(value, high_decimal_part, low_decimal_part=16):
       """Takes in low registers decimal count and high registers decimal count
         and the combined value and splits it to all the different parts"""
       low_mask = (2**low_decimal_part)-1
       high_mask = (2**high_decimal_part) - 1
       low_value = value & low_mask
       high_value = (value >> low_decimal_part) & high_mask
       return low_value, high_value

def get_twos_complement(bit, value):
       """Bit tells how manieth bit 2^n"""
       is_highest_bit_on = value & 1 << bit

       if is_highest_bit_on:
                base = 2**bit
                if bit == 0:
                        return -1
                lower_mask = (2**bit) -1
                lower = value & lower_mask
                return (lower - base)
                
       return value

def convert_vel_rpm_revs(rpm):
        """
        Takes in velocity rpm and converts it into revs 
        return tuple with higher register value first
        8.24 format
        """
        rpm = abs(rpm)
        try:
                rpm = int(rpm)
        except ValueError:
                raise
        if rpm > 1000:
                rpm = 1000
        
        revs = rpm/60.0
        return convert_val_into_format(revs, format="8.24")

def convert_acc_rpm_revs(rpm):
        """
        Takes in acceleration rpm and converts it into revs 
        return tuple with higher register value first
        12.20 format
        """
        rpm = abs(rpm)
        try:
                rpm = int(rpm)
        except ValueError:
                raise
        
        if rpm > 2000:
                rpm = 2000
        
        revs = rpm/60.0
        return convert_val_into_format(revs, "12.20")

def get_current_path(file):
        return Path(file).parent

def bit_high_low_both(number, low_bit, output="both"):
        low_mask = (2**low_bit) - 1
        register_val_high = number >> low_bit
        register_val_low = number & low_mask
        if output=="both":
                return (register_val_high, register_val_low)
        elif output == "high":
                return register_val_high
        elif output == "low":   
                return register_val_low
        else:
                raise Exception
        

def setup_logger(logger):
        """
        Setup logger for the MotorApi class.
        If no logger is provided, creates a basic console logger.
        """
        if logger is not None:
                return logger

        # Create a new logger
        logger = logging.getLogger(f"{__name__}")
        logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers if logger already exists
        if not logger.handlers:
                # Create console handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                
                # Create formatter
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)
                
                # Add handler to logger
                logger.addHandler(console_handler)

        return logger
        