import serial


class ArduinoBoard:
    def __init__(self) -> None:
        self.arduino = serial.Serial(port="COM8", baudrate=9600, timeout=0.1)

    def send_command(self, cmd):
        # Send data to Arduino
        self.arduino.write(bytes(cmd, "utf-8"))  # Send with newline

        # Wait for a response
        while True:
            data = self.arduino.readline().decode("utf-8").strip()
            if data:  # Check if data is received
                return data
