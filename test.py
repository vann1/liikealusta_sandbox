from utils import is_nth_bit_on
high_decimal = 2560 >> 7

HOME_PRIMARY_OPTIONS_VAL = 59343
v = is_nth_bit_on(1, HOME_PRIMARY_OPTIONS_VAL)
u = is_nth_bit_on(0, HOME_PRIMARY_OPTIONS_VAL)


a = 20
# print(moi)
velocity_left = high_decimal >> 8
b = 10

def bit_high_low(number, low_bit):
    bit_mask = (2**low_bit) - 1
    register_val_high = number >> low_bit
    register_val_low = number & bit_mask
    return (register_val_high, register_val_low)

result = bit_high_low(405, 8)
result2 = bit_high_low(32, 4)

d = 384 >> 7

a = 38 >> 8
b = a // 2
c = 20

a = 10

