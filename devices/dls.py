import csv
import time
import serial
from tqdm import tqdm

from .utils import RequestFailed, UnexpectedResponse, ErrorOccurred


class DLS_Analyzer:
    """
    A class to interface with a DLS (Dynamic Light Scattering) analyzer through a serial connection.

    This class provides methods for initializing the serial connection, sending commands to
    the DLS device, and handling communication with the device. It is intended for controlling
    and interacting with a DLS analyzer through RS232 serial communication.

    Attributes:
        port (str): The serial port to connect to (default is "COM7").
        baudrate (int): The baud rate for the serial connection (default is 9600).
        timeout (int): The timeout period (in seconds) for reading from the serial port (default is 1).
        feedback (str or None): Stores the response from the DLS device after sending a command.
    """

    def __init__(self, port="COM7", baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.feedback = None

    def initialize(self):
        """
        Initializes the serial connection to the DLS device.

        This method sets up the serial communication using the specified port,
        baudrate, and timeout. The connection is established via the `serial.Serial`
        interface, enabling communication with the device.
        """

        self.dls_ser = serial.Serial(
            port=self.port, baudrate=self.baudrate, timeout=self.timeout
        )

    def send_command(self, cmd: bytes, timeout=5):
        """
        Sends a command to the DLS device and waits for a response.

        This method writes the given command to the DLS device, waits for a response
        within the specified timeout period, and returns the feedback received from the
        device. If no response is received within the timeout, a `TimeoutError` is raised.

        Args:
            cmd (bytes): The command to send to the DLS device.
            timeout (int, optional): The maximum time to wait for a response, in seconds. Defaults to 5 seconds.

        Returns:
            str: The feedback received from the device, decoded as a UTF-8 string.

        Raises:
            TimeoutError: If no response is received within the specified timeout.
        """

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
        Verifies that the RS232 communications link is active.

        This method sends a dummy command to ensure that the RS232 communications
        link is present and operational. If the device responds, communications
        are considered successfully established.

        Args:
            None

        Raises:
            UnexpectedResponse: If the device returns an unexpected response.
        """

        cmd = bytes([0x31])
        feedback = self.send_command(cmd=cmd)
        if feedback == "K":
            print("COM Check Successful")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def select_measurement_setup(self, setup_index: int):
        """
        Selects a measurement setup from the scheduler.

        This method selects a measurement setup by index (1, 2, ...) and applies
        the corresponding parameters to the next `setzero` or `run` command.
        The selected setup remains active for all subsequent measurements until
        either another measurement setup is selected or a local change to the
        measurement setup is made.

        Args:
            setup_index (int): The index of the measurement setup to select.

        Raises:
            RequestFailed: If the selection process fails and the device returns 'N'.
            UnexpectedResponse: If the device returns an unexpected response.
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
        Initiates the Setzero function for a measurement with no sample present.

        This method starts a Setzero process, which must complete before other
        commands can be sent. The status of the Setzero process is returned once
        it is finished.

        Args:
            None

        Raises:
            RequestFailed: If the Setzero process fails with 'High Background' (response 'N').
            UnexpectedResponse: If the device returns an unexpected response.
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
        Initiates the Sample Loading function.

        This method prepares the device for a sample measurement. For Diffraction
        Analyzers, ensure that auto-dilution is enabled in the Sample Loading
        section of the Auto-Sequence Tab of the SOP.

        Args:
            None

        Raises:
            UnexpectedResponse: If the device returns an unexpected response.
        """

        cmd = bytes([0x3A])
        feedback = self.send_command(cmd=cmd, timeout=10)
        if feedback == "K":
            print("Sample Loading Successful")
        else:
            raise UnexpectedResponse(f"Unexpected response received: {feedback}")

    def run(self):
        """
        Initiates a sample measurement run.

        This method starts a measurement with a sample present. No other commands
        can be sent until the HOST computer returns the measurement status. The
        method checks the response and raises exceptions if the run fails or an
        error occurs.

        Args:
            None

        Raises:
            RequestFailed: If the measurement run fails (response 'N').
            ErrorOccurred: If an error occurs on the HOST PC (response 'E').
            UnexpectedResponse: If the device returns an unexpected response.
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

    def request_data(self, num_of_runs: int, data_file="measurement.csv"):
        """
        Perform multiple measurements, collect requested data, and save results in a .csv file.

        This method runs multiple measurements, collects data for each measurement (e.g.,
        mean diameters and percentiles), and stores the results in a specified CSV file.
        After completing the measurements, it calculates and appends average values for each
        data point.

        Args:
            num_of_runs (int): The number of measurements to perform.
            data_file (str, optional): The file path where the data will be saved. Defaults to "measurement.csv".

        Raises:
            RequestFailed: If any of the measurements fail or return invalid data (response 'N').
            UnexpectedResponse: If the device returns an unexpected response.
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
                    # Error handle
                    if feedback_list[0] == "K":
                        pass
                    elif feedback_list[0] == "N":
                        raise RequestFailed("Invalid Data Request")
                    else:
                        raise UnexpectedResponse(
                            f"Unexpected response received: {feedback_list[0]}"
                        )
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
