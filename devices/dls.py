import csv
import time
import serial
from tqdm import tqdm

from .utils import RequestFailed, UnexpectedResponse, ErrorOccurred


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
        """
        Dummy command to insure that the RS232 communications link is
        present and working. If a response is received after sending this
        command then communications has been successfully established.

        Returns 'K' if communications is OK otherwise Nothing is returned (Time Out)
        """

        cmd = bytes([0x31])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("COM Check Successful")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def select_measurement_setup(self, setup_index):
        """
        Selects a Measurement Setup from the Scheduler with index (1, 2, ...).
        Setup parameters are applied to next Setzero or Run and remain the same
        for all subsequent measurements until changed via another Select
        Measurement Setup command or a local change to Measurement
        Setup is performed.

        Returns 'K' if successful or 'N' if unsuccessful.
        """

        cmd = bytes([0x36, setup_index])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("Measurement Setup Selection Successful")
        elif feedback == "N":
            raise RequestFailed("Measurement Setup Selection Failed")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def set_zero(self):
        """
        Initiate Setzero function (measurement with no sample present). No
        other commands can be sent until the Host computer returns the
        Setzero Status.

        Returns the status of the Setzero after a Setzero has completed
        'K' if pass or 'N' if fail with 'High Background'.
        """

        cmd = bytes([0x33])
        feedback = self.send_command(cmd=cmd, timeout=60)
        if feedback == "K":
            print("Set Zero Successful")
        elif feedback == "N":
            raise RequestFailed("Set Zero Failed: High Background")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def sample_loading(self):
        """
        Initiate the Sample Loading function. For Diffraction Analyzers make
        sure that auto-dilute is enabled in the Sample Loading section of the
        Auto-Sequence Tab of the SOP.

        Returns 'K' when Sample Loading Form closes.
        """

        cmd = bytes([0x3A])
        feedback = self.send_command(cmd=cmd, timeout=10)
        if feedback == "K":
            print("Sample Loading Successful")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def run(self):
        """
        Initiate a sample measurement Run function (measurement with
        sample present). No other commands can be sent until the HOST
        computer returns the Measurement Status.

        Returns 'K' if successful or 'N' if unsuccessful or 'E' if error has occurred on the HOST PC.
        """

        cmd = bytes([0x34])
        feedback = self.send_command(cmd=cmd, timeout=500)
        if feedback == "K":
            pass
        elif feedback == "N":
            raise RequestFailed("Sample Measurement Failed")
        elif feedback == "E":
            raise ErrorOccurred("Error has occurred on the HOST PC")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def request_data(self, num_of_runs, data_file="measurement.csv"):
        """
        Perform multiple measurements, collect requested data, and save results in a .csv file.
        """

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

        headers = [
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
        ]

        accumulated_data = [0.0] * (len(headers) - 2)
        with open(data_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for run_id in tqdm(range(num_of_runs), desc="Measurements Running: "):
                # Run measurement once
                self.run()
                data_line = [time.asctime(), run_id + 1]

                for cmd in cmds:
                    feedback = self.send_command(cmd=cmd)
                    feedback_list = str(feedback).split(" ")
                    # Extract the Percentile Value from Percentile
                    if len(feedback_list) != 2:
                        for i in range(len(feedback_list)):
                            if i % 2 == 0 and i > 0:
                                data_line.append(feedback_list[i])
                    # Extract Data Value
                    else:
                        data_line.append(feedback_list[1])
                # print(data_line)
                writer.writerow(data_line)

                # Accumulate each measurement data
                for j in range(len(headers) - 2):
                    accumulated_data[j] += float(data_line[j + 2])

            # Calculate average values
            last_line = [time.asctime(), "Avg."]
            for k in range(len(headers) - 2):
                avg_val = accumulated_data[k] / num_of_runs
                last_line.append(f"{avg_val:.1f}")
            writer.writerow(last_line)


if __name__ == "__main__":
    dls = DLS_Analyzer()
    dls.initialize()
    time.sleep(1)
    dls.com_check()
    time.sleep(1)
    dls.select_measurement_setup(5)

    time.sleep(1)
    dls.request_data(num_of_runs=10)
