from sandbox import Sandbox

sandbox = Sandbox()

def test_ucur16():
    assert sandbox.registers_convertion([32768], "9.7") == 256.0
    
    result = sandbox.registers_convertion([65535], "9.7")
    expected = 511.9921
    diff = result - expected 
    assert diff < 0.001

    assert sandbox.registers_convertion([0], "9.7") == 0.0
    assert sandbox.registers_convertion([128], "9.7") == 1.0
    assert sandbox.registers_convertion([128+64], "9.7") == 1.5
    assert sandbox.registers_convertion([128+32], "9.7") == 1.25

def test_ucur32():
    result = sandbox.registers_convertion([65535, 65535], "8.24")
    expected = 511.999
    diff = result - expected
    assert diff < 0.001

    assert sandbox.registers_convertion([32768], "9.7") == 256.0

    result = sandbox.registers_convertion([65535, 127], "9.23")
    expected = 0.999999
    diff = result - expected
    assert diff < 0.001
    assert sandbox.registers_convertion([0, 128], "9.23") == 1.0

def test_uvel32():
    result = sandbox.registers_convertion([65535, 65535], "8.24")
    expected = 255.999
    diff = result - expected
    assert diff < 0.001

    result = sandbox.registers_convertion([0, 256], "8.24") == 1.0
    result = sandbox.registers_convertion([0, 512], "8.24") == 2.0
    result = sandbox.registers_convertion([0, 0], "8.24") == 0.0

def test_uacc32():
    result = sandbox.registers_convertion([65535, 65535], "12.20")
    expected = 4095.999
    diff = result - expected
    assert diff < 0.001

    assert sandbox.registers_convertion([0, 16], "12.20") == 1.0
    assert sandbox.registers_convertion([0, 32], "12.20") == 2.0
    assert sandbox.registers_convertion([0, 48], "12.20") == 3.0

def test_uvolt32():
    result = sandbox.registers_convertion([65535, 65535], "11.21")
    expected = 2047.999
    diff = result - expected
    assert diff < 0.001

    assert sandbox.registers_convertion([0, 32], "11.21") == 1.0
    assert sandbox.registers_convertion([0, 64], "11.21") == 2.0
    assert sandbox.registers_convertion([0, 96], "11.21") == 3.0

def test_pos32():
    assert sandbox.registers_convertion([0, 32768], "16.16", signed=True) == -32768
    result = sandbox.registers_convertion([65535, 65535], "16.16", signed=True)
    expected = 0
    diff = result - expected < 0.001

    assert sandbox.registers_convertion([0, 16], "16.16", signed=True) == 16.0

    result = sandbox.registers_convertion([65535, 16], "16.16", signed=True)
    expected = 16.9999847
    diff = result - expected 
    assert diff < 0.001

    assert sandbox.registers_convertion([32768, 16], "16.16", signed=True) == 16.5
    assert sandbox.registers_convertion([32768, 0], "16.16", signed=True) == 0.5

    result = sandbox.registers_convertion([10000, 3], "16.16", signed=True)
    expected = 3.1525878
    diff = result - expected 
    assert diff < 0.001

def test_volt32():
    assert sandbox.registers_convertion([0, 32768], "11.21", signed=True) == -1024.0

    result = sandbox.registers_convertion([65535, 65535], "11.21", signed=True)
    expected = 0
    diff = result - expected 
    assert diff < 0.001

    assert sandbox.registers_convertion([0, 32], "11.21", signed=True) == 1.0
    assert sandbox.registers_convertion([0, 64], "11.21", signed=True) == 2.0
    assert sandbox.registers_convertion([0, 64], "11.21", signed=True) == 2.0
    assert sandbox.registers_convertion([0, 32+32768], "11.21", signed=True) == -1023.0
    assert sandbox.registers_convertion([0, 32+64+32768], "11.21", signed=True) == -1021.0

result = sandbox.registers_convertion([0, 32+32768], "11.21", signed=True)
a =10
# result = sandbox.registers_convertion([65535, 16], "16.16", 3)
# a = 10

# result = sandbox.registers_convertion([0, 32768], "16.16", signed=True)
# expected = 32767.999
# diff = result - expected
# assert diff < 0.001