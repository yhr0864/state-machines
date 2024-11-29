import csv
import time
import serial


class DLS_Analyzer:
    def __init__(self, port="COM7", baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.feedback = None

    def initialize(self):
        self.dls_ser = serial.Serial(
            port=self.port, baudrate=self.baudrate, timeout=self.timeout
        )

    def send_command(self, cmd, timeout=5):
        # Send command to DLS
        self.dls_ser.write(cmd)

        start_time = time.time()

        # Wait for a response
        while time.time() - start_time < timeout:
            # Check if get feedback
            if self.dls_ser.in_waiting:
                self.feedback = self.dls_ser.readline().decode("utf-8").strip()
                # self.feedback = self.dls_ser.read(200).decode("utf-8").strip()
                if self.feedback:
                    return self.feedback
        else:
            raise TimeoutError("No response from DLS within the specified timeout.")

    def com_check(self):
        cmd = bytes([0x31])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("COM Check Successful")
        elif feedback == "N":
            print("COM Check failed")
        else:
            print(f"Unexpected response received: {feedback}")

    def select_measurement_setup(self, setup_index):
        cmd = bytes([0x36, setup_index])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("Measurement Setup Selection Successful")
        elif feedback == "N":
            print("Measurement Setup Selection Failed")
        else:
            print(f"Unexpected response received: {feedback}")

    def set_title(self, title: str):
        cmd = bytes([0x30]) + title.encode("ascii")
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("Set Title Successful")
        elif feedback == "N":
            print("Set Title Failed")
        else:
            print(f"Unexpected response received: {feedback}")

    def background_check(self):
        cmd = bytes([0x35])
        feedback = self.send_command(cmd=cmd, timeout=30)
        if feedback == "K":
            print("Background Check Successful")
        elif feedback == "N":
            print("Background Check Failed")
        else:
            print(f"Unexpected response received: {feedback}")

    def set_zero(self):
        cmd = bytes([0x33])
        feedback = self.send_command(cmd=cmd, timeout=60)
        if feedback == "K":
            print("Set Zero Successful")
        elif feedback == "N":
            print("Set Zero Failed: High Background")
        else:
            print(f"Unexpected response received: {feedback}")

    def sample_loading(self):
        cmd = bytes([0x3A])
        feedback = self.send_command(cmd=cmd, timeout=10)
        if feedback == "K":
            print("Sample Loading Successful")
        elif feedback == "N":
            print("Sample Loading Failed")
        else:
            print(f"Unexpected response received: {feedback}")

    def run(self):
        cmd = bytes([0x34])
        feedback = self.send_command(cmd=cmd, timeout=500)
        if feedback == "K":
            print("Sample Measurement Successful")
        elif feedback == "N":
            print("Sample Measurement Failed")
        else:
            print(f"Unexpected response received: {feedback}")

    def request_data(self):
        cmds = [
            # bytes([0x37, 1]),  # Request Data (Sample Loading)
            bytes([0x37, 2]),  # Request Data (Mean Volume Diameter (Mv))
            bytes([0x37, 3]),  # Request Data (Mean Area Diameter (Ma))
            bytes([0x37, 4]),  # Request Data (Mean Number Diameter (Mn))
            bytes([0x37, 5]),  # Request Data (Percentiles Values (s))
            # bytes([0x37, 6]),  # Request Data (Size Percent Value(s))
            # bytes([0x37, 7]),  # Request Data (Peaks Summary Value(s))
            # bytes([0x37, 8]),  # Request Data (Tabular Data)
            # bytes([0x37, 9]),  # Request Data (Zeta Potential)
        ]

        # # Show the bug
        # for cmd in cmds:
        #     feedback = self.send_command(cmd=cmd)
        #     print(feedback)

        with open("eggs.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Time",
                    "Run",
                    "Mean volume diameter",
                    "Mean area diameter",
                    "Mean number diameter",
                    "d(10%)",
                    "d(20%)",
                    "d(30%)",
                    "d(40%)",
                    "d(50%)",
                    "d(60%)",
                    "d(70%)",
                    "d(80%)",
                    "d(90%)",
                    "d(95%)",
                ],
            )
            data_line = [time.asctime(), 1]
            for cmd in cmds:
                feedback = self.send_command(cmd=cmd)
                feedback_list = str(feedback).split(" ")
                if len(feedback_list) != 2:
                    for i in range(len(feedback_list)):
                        if i % 2 == 0 and i > 0:
                            data_line.append(feedback_list[i])
                else:
                    data_line.extend(feedback_list[1:])
                # writer.writerow(str(feedback))
            # print(data_line)
            writer.writerow(data_line)


if __name__ == "__main__":
    dls = DLS_Analyzer()
    dls.initialize()
    time.sleep(1)
    dls.com_check()
    # time.sleep(1)
    # dls.select_measurement_setup(5)
    # time.sleep(1)
    # dls.set_title("measurement_2")
    # time.sleep(1)
    # dls.background_check()
    # time.sleep(1)
    # dls.set_zero()
    # dls.sample_loading()
    # time.sleep(1)
    # dls.run()
    # time.sleep(1)
    dls.request_data()
