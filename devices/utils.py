import serial
import time
from typing import Union


class SerialCommunication:
    """
    A class to handle serial communication with a target device.

    This class facilitates serial communication by initializing a connection to
    the device, sending commands, and receiving feedback.

    Attributes:
        device (str): The name or description of the device being communicated with.
        port (str): The serial port to connect to (default is "COM1").
        baudrate (int): The communication speed in bits per second (default is 9600).
        timeout (int): The timeout duration for the serial connection in seconds (default is 1).
        feedback (str or None): The response received from the device, if any.

    Methods:
        initialize():
            Initializes the serial connection with the specified port, baudrate, and timeout.
        send_command(cmd, timeout=5):
            Sends a command to the device and waits for a response within the specified timeout period.
    """

    def __init__(
        self, device: str, port: str = "COM1", baudrate: int = 9600, timeout: int = 1
    ):
        self.device = device
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.feedback = None

    def initialize(self):
        self.ser = serial.Serial(
            port=self.port, baudrate=self.baudrate, timeout=self.timeout
        )

    def send_command(self, cmd: Union[str, bytes], timeout=5):
        # Ensure the data type to write-in is always 'bytes'
        if isinstance(cmd, str):
            cmd = bytes(cmd, "utf-8")

        # Send command to target device
        self.ser.write(cmd)

        start_time = time.time()
        # Wait for a response
        while time.time() - start_time < timeout:
            # Check if get feedback
            if self.ser.in_waiting:
                self.feedback = self.ser.readline().decode("utf-8").strip()
                if self.feedback:
                    return self.feedback
        else:
            raise TimeoutError(
                f"No response from {self.device} within the specified timeout."
            )


class RequestFailed(Exception):
    """
    Raised when received 'N'.

    Received last command but there was a problem, invalid command
    was received or Status of a measurement was BAD.
    """

    pass


class UnexpectedResponse(Exception):
    """Raised when received unknown feedback"""

    pass


class ErrorOccurred(Exception):
    """
    Raised when received 'E'.

    Indicates an Error has occurred on the HOST PC that needs user
    attention. Usually this is a message box on the Host PC screen
    that needs to be “LOCALLY” acknowledged.
    """

    pass
