import sys
from pymodbus.client import ModbusTcpClient
from collections import deque
import utils as utils
import time as time
import matplotlib.pyplot as plt

class Scope():
    def __init__(self, arguments): #argumens trigger_register, trigger_register_format, trigger_register_signed, count, trigger_level
        self.arguments = arguments
        SERVER_IP_LEFT="192.168.0.211"
        SERVER_PORT=502
        client_left = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
        self.monitor_time = 10
        self.previous_time = None
        self.deltatime = None
        self.triggered = False
        self.plottable_points = None
        client_left.connect()
   
        # cmd line arguments
        self.trigger_register = 4306
        self.trigger_register_format = "8.24"
        self.trigger_register_signed = False
        self.count = 2
        self.trigger_level = 0.5
        self.window_size = 100
        
        # deque array for datapoints
        self.datapoint_1 = deque(maxlen=self.window_size)
        self.datapoint_2 = deque(maxlen=self.window_size)
        self.datapoint_3 = deque(maxlen=self.window_size)
        self.datapoint_4 = deque(maxlen=self.window_size)
        
        self.plottable_points_1 = None
        self.plottable_points_2 = None
        self.plottable_points_3 = None
        self.plottable_points_4 = None

        self.triggered = False
        
    def poll_data(self):
        proportional = self.client_left.read_holding_registers(address=5402, count=1)
        integral = self.client_left.read_holding_registers(address=5403, count=1)
        derivative = self.client_left.read_holding_registers(address=5405, count=1)
        trigger_value = self.client_left.read_holding_registers(address=self.trigger_register, count=self.count)
        return (proportional, integral, derivative,trigger_value)
    
    def draw_graph(self):
        while self.monitor_time > 0:
            if self.previous_time != None: 
                self.delta_time = time.time() - self.previous_time
                self.previous_time = time.time()
            else:
                self.previous_time = time.time()
            proportional, integral, derivative, trigger_value = self.poll_data()
            trigger_value = utils.registers_convertion(trigger_value.registers, self.trigger_register_format, self.trigger_register_signed)
            
            if not self.triggered:
                self.datapoint_1.append(proportional.registers[0])
                self.datapoint_2.append(integral.registers[0])
                self.datapoint_3.append(derivative.registers[0])
                self.datapoint_4.append(time.time())
            else:
                self.plottable_points_1.append(proportional.registers[0])
                self.plottable_points_2.append(integral.registers[0])
                self.plottable_points_3.append(derivative.registers[0])
                self.plottable_points_4.append(time.time())
            
            if self.triggered or trigger_value > 0.5:
                   if self.triggered == False:
                        self.plottable_points_1 = list(self.datapoint_1.copy)
                        self.plottable_points_2 = list(self.datapoint_2.copy)
                        self.plottable_points_3 = list(self.datapoint_3.copy)
                        self.plottable_points_4 = list(self.datapoint_4.copy)
                        self.triggered = True
                   else:
                        self.monitor_time -= self.delta_time
        
            time.sleep(0.05)
        plt.figure(figsize=(10,6))
        plt.plot(self.plottable_points_4, self.plottable_points_1, label="Proportional",color="red")
        plt.plot(self.plottable_points_4, self.plottable_points_2, label="Integral", color="green")
        plt.plot(self.plottable_points_4, self.plottable_points_3, label="Derivative", color="blue")
        plt.xlabel("Time")
        plt.ylabel("Values")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
if __name__ == "__main__":
    scope = Scope(sys.argv[1:])
    