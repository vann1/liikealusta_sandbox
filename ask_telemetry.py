from tcp_socket_client import TCPSocketClient
from time import sleep
from utils import extract_part
def recive_telemetry_data(message):
    message=extract_part("message=", message)
    pitch,roll = message.split(",")
    pitch = float(pitch)
    roll = float(roll)
    roll -= 0.6
    print(pitch,",",roll)


if __name__ == "__main__":
    tcp_client = TCPSocketClient(host="10.214.33.19", port=7001, on_message_received=recive_telemetry_data)
    tcp_client.connect()
    while True:
        tcp_client.send_message("action=r_xl|")
        sleep(1)
    
    
