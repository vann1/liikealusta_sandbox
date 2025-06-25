from tcp_socket_client import TCPSocketClient
from time import sleep
from utils import extract_part
from motionplatform_interface import MotionPlatformInterface

class CrazyDemo():
    telemetry_data_processed=True
    def recive_telemetry_data(self,message):
        message=extract_part("message=", message)
        pitch,roll = message.split(",")
        pitch = float(pitch)
        roll = float(roll)
        pitch -= 0.3
        roll -= 0.5
        pitch /= 5
        roll /= 3.5
        self.mpi.set_angles(pitch,roll)
        print(pitch,",",roll)
        self.telemetry_data_processed=True
        


    def init(self):
        self.mpi = MotionPlatformInterface()
        self.mpi.init()

if __name__ == "__main__":
    crazyDemo = CrazyDemo()
    crazyDemo.init() # Initializes mpi class
    tcp_client = TCPSocketClient(host="10.214.33.19", port=7001, on_message_received=crazyDemo.recive_telemetry_data)
    tcp_client.connect()

    while True:
        if crazyDemo.telemetry_data_processed:
            crazyDemo.telemetry_data_processed=False
            tcp_client.send_message("action=r_xl|")
            sleep((1/5))
        
        
