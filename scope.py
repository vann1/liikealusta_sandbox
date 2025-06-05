import sys
from pymodbus.client import ModbusTcpClient
from collections import deque
import utils as utils
import time as time
import matplotlib.pyplot as plt

class Scope():
    def __init__(self):
        SERVER_IP_LEFT="192.168.0.211"
        SERVER_PORT=502
        self.client_left = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
        self.monitor_time = 10
        self.previous_time = None
        self.triggered = False
        self.plottable_points = None
        self.client_left.connect()
        self.delta_time = 0
   
        # cmd line arguments
        self.trigger_register = 344
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
        self.datapoint_5 = deque(maxlen=self.window_size)
        self.datapoint_6 = deque(maxlen=self.window_size)
        self.time = deque(maxlen=self.window_size)
        
        self.plottable_points_1 = None
        self.plottable_points_2 = None
        self.plottable_points_3 = None
        self.plottable_points_4 = None
        self.plottable_points_5 = None
        self.plottable_points_6 = None
        self.plottable_time = None

        self.triggered = False
        
    def poll_data(self):
        proportional = self.client_left.read_holding_registers(address=5402, count=1)
        integral = self.client_left.read_holding_registers(address=5403, count=1)
        derivative = self.client_left.read_holding_registers(address=5405, count=1)
        perror = self.client_left.read_holding_registers(address=382, count=2)
        pfeedback = self.client_left.read_holding_registers(address=378, count=2)
        pcommand = self.client_left.read_holding_registers(address=380, count=2)
        trigger_value = self.client_left.read_holding_registers(address=self.trigger_register, count=self.count)
        return (proportional, integral, derivative,perror,pfeedback,pcommand,trigger_value)
    
    def draw_graph(self):
        while self.monitor_time > 0:
            if self.previous_time != None: 
                self.delta_time = time.time() - self.previous_time
                self.previous_time = time.time()
            else:
                self.previous_time = time.time()
            proportional, integral, derivative, perror,pfeedback,pcommand, trigger_value = self.poll_data()
            trigger_value = utils.registers_convertion(trigger_value.registers, format="8.24", signed=True)
            trigger_value = abs(trigger_value)
            perror = utils.registers_convertion(register=perror.registers, format="16.16", signed=True)
            pfeedback = utils.registers_convertion(register=pfeedback.registers, format="16.16", signed=True)
            pcommand = utils.registers_convertion(register=pcommand.registers, format="16.16", signed=True)

            if not self.triggered:
                self.datapoint_1.append(proportional.registers[0])
                self.datapoint_2.append(integral.registers[0])
                self.datapoint_3.append(derivative.registers[0])
                self.datapoint_4.append(perror)
                self.datapoint_5.append(pfeedback)
                self.datapoint_6.append(pcommand)
                self.time.append(time.time())
            else:
                self.plottable_points_1.append(proportional.registers[0])
                self.plottable_points_2.append(integral.registers[0])
                self.plottable_points_3.append(derivative.registers[0])
                self.plottable_points_4.append(perror)
                self.plottable_points_5.append(pfeedback)
                self.plottable_points_6.append(pcommand)
                self.plottable_time.append(time.time())
            
            if self.triggered or trigger_value > 0.5:
                   if self.triggered == False:
                        self.plottable_points_1 = list(self.datapoint_1.copy())
                        self.plottable_points_2 = list(self.datapoint_2.copy())
                        self.plottable_points_3 = list(self.datapoint_3.copy())
                        self.plottable_points_4 = list(self.datapoint_4.copy())
                        self.plottable_points_5 = list(self.datapoint_5.copy())
                        self.plottable_points_6 = list(self.datapoint_6.copy())
                        self.plottable_time = list(self.time.copy())
                        self.triggered = True
                   else:
                        self.monitor_time -= self.delta_time
        
            time.sleep(0.05)
        plt.figure(figsize=(10,6))
        # plt.plot(self.plottable_time, self.plottable_points_1, label="Proportional",color="brown")
        # plt.plot(self.plottable_time, self.plottable_points_2, label="Integral", color="orange")
        # plt.plot(self.plottable_time, self.plottable_points_3, label="Derivative", color="green")
        # plt.plot(self.plottable_time, self.plottable_points_4, label="Perror", color="red")
        plt.plot(self.plottable_time, self.plottable_points_5, label="Current position", color="green")
        plt.plot(self.plottable_time, self.plottable_points_6, label="Target position", color="red")

        plt.xlabel("Time")
        plt.ylabel("Values")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('scope.png')
        # plt.style.use('fivethirtyeight')
        plt.show()
if __name__ == "__main__":
    scope = Scope()
    scope.draw_graph()
    