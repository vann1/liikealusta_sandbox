import sys
from pymodbus.client import ModbusTcpClient
from collections import deque
import utils as utils
import time as time
import matplotlib.pyplot as plt
from motors_config import MotorConfig
config = MotorConfig()

class Scope():
    def __init__(self):
        SERVER_IP_LEFT="192.168.0.211"
        SERVER_PORT=502
        self.client_left = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
        self.monitor_time = 15
        self.previous_time = None
        self.triggered = False
        self.plottable_points = None
        self.client_left.connect()
        self.delta_time = 0
   
        # cmd line arguments
        # self.trigger_register = 344
        self.trigger_register = 360
        self.trigger_register_format = "8.24"
        self.trigger_register_signed = True
        self.count = 2
        self.trigger_level = 0.0
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
        
    def poll_data(self): # Idisplay
        idisplay = self.client_left.read_holding_registers(address=566, count=2)
        perror = self.client_left.read_holding_registers(address=382, count=2)
        host_velocity = self.client_left.read_holding_registers(address=4306, count=2)
        pfeedback = self.client_left.read_holding_registers(address=378, count=2)
        vfeedback = self.client_left.read_holding_registers(address=344, count=2)
        wtf = self.client_left.read_holding_registers(address=360, count=2)
        host_acc = self.client_left.read_holding_registers(address=4308, count=2)
        analog_vel = self.client_left.read_holding_registers(address=config.ANALOG_VEL_MAXIMUM, count=2)
        oeg_motion = self.client_left.read_holding_registers(address=105, count=1)

        trigger_value = self.client_left.read_holding_registers(address=self.trigger_register, count=self.count)
        return (idisplay,perror,host_velocity,pfeedback,trigger_value,vfeedback,host_acc, analog_vel,oeg_motion, wtf)
    
    def draw_graph(self):
        while self.monitor_time > 0:
            if self.previous_time != None: 
                self.delta_time = time.time() - self.previous_time
                self.previous_time = time.time()
            else:
                self.previous_time = time.time()
            idisplay,perror,host_velocity,pfeedback,trigger_value,vfeedback, host_acc, analog_vel,oeg_motion,wtf = self.poll_data()
            trigger_value = utils.registers_convertion(trigger_value.registers, format=self.trigger_register_format, signed=self.trigger_register_signed)
            trigger_value = abs(trigger_value)
            perror = utils.registers_convertion(register=perror.registers, format="16.16", signed=True)
            host_velocity = utils.registers_convertion(register=host_velocity.registers, format="8.24", signed=True)
            vfeedback = utils.registers_convertion(register=vfeedback.registers, format="8.24", signed=True)
            wtf = utils.registers_convertion(register=wtf.registers, format="8.24", signed=True)
            host_acc = utils.registers_convertion(register=host_acc.registers, format="12.20", signed=False)
            analog_vel = utils.registers_convertion(register=analog_vel.registers, format="8.24", signed=False)
            pfeedback = utils.registers_convertion(register=pfeedback.registers, format="16.16", signed=True)
            idisplay = utils.registers_convertion(register=idisplay.registers, format="9.23", signed=True)
            in_position = utils.is_nth_bit_on(12,oeg_motion.registers[0])
            host_velocity *= 60
            analog_vel *= 60
            vfeedback *= 60
            host_acc *= 60
            if not self.triggered:
                self.datapoint_1.append(wtf)
                self.datapoint_2.append(vfeedback)
                self.datapoint_3.append(analog_vel)
                self.datapoint_4.append(idisplay)
                self.time.append(time.time())
            else:
                self.plottable_points_1.append(wtf)
                self.plottable_points_2.append(vfeedback)
                self.plottable_points_3.append(analog_vel)
                self.plottable_points_4.append(idisplay)
                self.plottable_time.append(time.time())
            
            if self.triggered or trigger_value > self.trigger_level:
                   if self.triggered == False:
                        self.plottable_points_1 = list(self.datapoint_1.copy())
                        self.plottable_points_2 = list(self.datapoint_2.copy())
                        self.plottable_points_3 = list(self.datapoint_3.copy())
                        self.plottable_points_4 = list(self.datapoint_4.copy())
                        self.plottable_time = list(self.time.copy())
                        self.triggered = True
                   else:
                        self.monitor_time -= self.delta_time
        
            time.sleep(0.05)
        plt.figure(figsize=(10,6))
        plt.figure(1)
        plt.plot(self.plottable_time, self.plottable_points_4, label="Idisplay",color="blue")
        plt.legend()
        plt.figure(2)
        plt.plot(self.plottable_time, self.plottable_points_2, label="vfeedback", color="green")
        plt.legend()
        plt.figure(3)
        plt.plot(self.plottable_time, self.plottable_points_3, label="Analog Velocity", color="orange")
        plt.legend()
        plt.figure(4)
        plt.plot(self.plottable_time, self.plottable_points_1, label="in_position", color="red")
        plt.xlabel("Time")
        plt.ylabel("Values")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.style.use('fivethirtyeight')
        plt.show()
if __name__ == "__main__":
    scope = Scope()
    scope.draw_graph()
    