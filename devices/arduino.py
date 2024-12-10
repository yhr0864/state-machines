import serial
import time


class ArduinoBoard:
    def __init__(self, port="COM14", baudrate=9600, timeout=0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.feedback = None

    def initialize(self):
        self.arduino = serial.Serial(
            port=self.port, baudrate=self.baudrate, timeout=self.timeout
        )

    def send_command(self, cmd, timeout=10):
        # Send command to Arduino
        self.arduino.write(bytes(cmd, "utf-8"))

        start_time = time.time()
        # Wait for a response
        while time.time() - start_time < timeout:
            # Check if get feedback
            if self.arduino.in_waiting:
                self.feedback = self.arduino.readline().decode("utf-8").strip()
                if self.feedback:
                    return self.feedback
        else:
            raise TimeoutError("No response from Arduino within the specified timeout.")


if __name__ == "__main__":
    arduino = ArduinoBoard()
    arduino.initialize()
    time.sleep(1)
    f = arduino.send_command("motor1 home")
    print(f)
