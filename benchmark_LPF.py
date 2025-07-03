
from tcp_socket_client import TCPSocketClient
from time import sleep
from utils import extract_part
from motionplatform_interface import MotionPlatformInterface

class Benchmark():
    def __init__(self, compare = False):
        self.lpf_file_path = "LPF_benchmark.txt"
        self.wo_lpf_file_path = "wo_LPF_benchmark.txt"
        self.results_file = "lpf_compare_results.txt"
        self.test_file_path="test.txt"
        self.lpf_file = None
        self.wo_lpf_file = None
        self.compare = compare
        self.alpha = .1
        self.first_reading = True

    telemetry_data_processed=True

    def calculate_diff_avgs(self, pitch_diffs, roll_diffs):
        pitch_diff_sum = 0
        roll_diff_sum = 0

        for p_diff in pitch_diffs:
            pitch_diff_sum += p_diff

        for r_diff in roll_diffs:
            roll_diff_sum += r_diff

        pitch_diff_avg = 0
        roll_diff_avg = 0
        print(f"Roll diff sum {roll_diff_sum}")
        print(f"Pitch diff sum {pitch_diff_sum}")

        pitch_diff_avg = pitch_diff_sum / len(pitch_diffs)
        roll_diff_avg = roll_diff_sum /  len(roll_diffs)

        return pitch_diff_avg, roll_diff_avg

    def update(self, new_pitch, new_roll):
        if self.first_reading:
            self.filtered_pitch = new_pitch
            self.filtered_roll = new_roll
            self.first_reading = False
        else:
            self.filtered_pitch = self.alpha * new_pitch + (1 - self.alpha) * self.filtered_pitch
            self.filtered_roll = self.alpha * new_roll + (1 - self.alpha) * self.filtered_roll
        
        return self.filtered_pitch, self.filtered_roll

    def recive_telemetry_data(self,message):
        message=extract_part("message=", message)
        pitch,roll = message.split(",")
        pitch = float(pitch)
        roll = float(roll)
        roll, pitch = self.update(roll, pitch)
        self.test_file.write(f"{pitch}|{roll}\n")
        self.test_file.flush()
        sleep(.1)
        print("got here?")
        self.telemetry_data_processed=True

    def init(self):
        self.results_file = open(self.results_file, "a")
        if self.compare:
            self.test_file = open(self.test_file_path, "r")
            # self.wo_lpf_file = open(self.wo_lpf_file_path, "r")
            # self.lpf_file = open(self.wo_lpf_file_path, "r")
        else:
            self.test_file = open(self.test_file_path, "w")
            pass
            # self.wo_lpf_file = open(self.wo_lpf_file_path, "w")
            # self.lpf_file = open(self.lpf_file_path, "w")

    
    def compare_diffs(self):
        # First file processing
        i = 0
        prev_pitch = None
        prev_roll = None
        pitch_diffs = []
        roll_diffs = []
        
        for line in self.test_file.readlines():
            i += 1
            data = line.strip().split("|")  # Added strip() to remove whitespace
            pitch = float(data[0])  # Convert to float
            roll = float(data[1])   # Convert to float
            
            if prev_pitch is None:  # More explicit None check
                prev_pitch = pitch
                prev_roll = roll
                continue
            else:
                pitch_diff = abs(prev_pitch - pitch)
                roll_diff = abs(prev_roll - roll)
                pitch_diffs.append(pitch_diff)
                roll_diffs.append(roll_diff)
                prev_roll = roll
                prev_pitch = pitch
                
            if i == 1001:
                break
        
        pitch_diff_avg, roll_diff_avg = self.calculate_diff_avgs(roll_diffs=roll_diffs, pitch_diffs=pitch_diffs)
        self.results_file.write(f"{pitch_diff_avg}|{roll_diff_avg}\n")
        
        # # Second file processing - RESET variables
        # i = 0  # Reset counter
        # prev_pitch = None
        # prev_roll = None
        # pitch_diffs = []
        # roll_diffs = []
        
        # for line in self.wo_lpf_file.readlines():
        #     i += 1
        #     data = line.strip().split("|")
        #     pitch = float(data[0])
        #     roll = float(data[1])
            
        #     if prev_pitch is None:
        #         prev_pitch = pitch
        #         prev_roll = roll
        #         continue
        #     else:
        #         pitch_diff = abs(prev_pitch - pitch)
        #         roll_diff = abs(prev_roll - roll)
        #         pitch_diffs.append(pitch_diff)
        #         roll_diffs.append(roll_diff)
        #         prev_roll = roll
        #         prev_pitch = pitch
                
        #     if i == 1001:
        #         break
        
        # pitch_diff_avg, roll_diff_avg = self.calculate_diff_avgs(roll_diffs=roll_diffs, pitch_diffs=pitch_diffs)
        # self.results_file.write(f"{pitch_diff_avg}|{roll_diff_avg}\n")
        
        # self.lpf_file.close()
        # self.wo_lpf_file.close()
        self.results_file.close()

if __name__ == "__main__":
    benchmark = Benchmark(compare=True)
    benchmark.init()
    benchmark.compare_diffs()
    # tcp_client = TCPSocketClient(host="10.214.33.19", port=7001, on_message_received=benchmark.recive_telemetry_data)
    # tcp_client.connect()

    # while True:
    #     if benchmark.telemetry_data_processed:
    #         benchmark.telemetry_data_processed=False
    #         tcp_client.send_message("action=r_xl|")
    #         sleep(0.1)
