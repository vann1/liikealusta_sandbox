from sandbox import Sandbox

sandbox = Sandbox()

def test_pos32():
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


# result = sandbox.registers_convertion([65535, 16], "16.16", 3)
# a = 10