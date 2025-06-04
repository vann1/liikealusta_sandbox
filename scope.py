import sys
from pymodbus.client import ModbusTcpClient
from collections import deque
import utils as utils
import time as time
import matplotlib.pyplot as plt

class Scope():
    def __init__(self, arguments): #argumens trigger_register, trigger_register_format, trigger_register_signed, count, trigger_value
        self.arguments = arguments
        SERVER_IP_LEFT="192.168.0.211"
        SERVER_PORT=502
        client_left = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
        client_left.connect()
        # deque array for datapoints
        self.window = deque(maxlen=100)
        # cmd line arguments
        self.trigger_register = int(arguments[0])
        self.trigger_register_format = arguments[1]
        self.trigger_register_signed = arguments[2]
        self.count = int(arguments[3])
        self.trigger_value = float(arguments[4])
        
        # Initialize the plot
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("test")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Values")
        self.ax.grid(True)
        
        # Initialize empty plot lines
        self.line_p, = self.ax.plot([], [], 'b-', label='Proportional')
        self.line_i, = self.ax.plot([], [], 'r-', label='Integral')
        self.line_d, = self.ax.plot([], [], 'g-', label='Derivative')
        self.ax.legend()

        self.start_time = time.time()
        self.triggered = False
        
    def poll_data(self):
        proportional = self.client_left.read_holding_registers(address=5402, count=1)
        integral = self.client_left.read_holding_registers(address=5403, count=1)
        derivative = self.client_left.read_holding_registers(address=5405, count=1)
        trigger = self.client_left.read_holding_registers(address=self.trigger_register, count=self.count)
        return (proportional, integral, derivative,trigger)
    
    def draw_graph(self):
        while True:
            proportional, integral, derivative, trigger = self.poll_data()
            trigger = utils.registers_convertion(trigger.registers[0], self.trigger_register_format, self.trigger_register_signed)
            current_time = time.time() - self.start_time
            self.window.append((proportional.registers[0], integral.registers[0], derivative.registers[0], current_time))
            if trigger > self.trigger_value and not self.triggered:
                    self.triggered = True
            if self.triggered:
                pass
                
            
            
            time.sleep(0.05)

if __name__ == "__main__":
    scope = Scope(sys.argv[1:])
    