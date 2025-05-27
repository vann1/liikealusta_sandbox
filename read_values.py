from pymodbus.client import ModbusTcpClient
import asyncio


SERVER_URL = "http://127.0.0.1:5001/"
SERVER_IP_LEFT="192.168.0.211"
SERVER_IP_RIGHT="192.168.0.212"
SERVER_PORT=502
client_leFt = ModbusTcpClient(host=SERVER_IP_LEFT, port=SERVER_PORT)
client_right = ModbusTcpClient(host=SERVER_IP_RIGHT, port=SERVER_PORT)

client_right.connect()
client_leFt.connect()

def main():
    try:
        while(True):
            
    except Exception as e:
        print(f"Error while reading registers: {e}")

if __name__ == "__main__":
     main()