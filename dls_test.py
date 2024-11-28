import serial
import serial.tools.list_ports
import time


ports = serial.tools.list_ports.comports()

# Print all the connected USB ports
# for port in ports:
#     print(f"Port: {port.device}, Description: {port.description}, HWID: {port.hwid}")

# Open the virtual COM port
ser = serial.Serial(
    port="COM7",  # This might be /dev/ttyUSB0 depending on your setup
    baudrate=9600,  # Set this according to your device's specification
    timeout=1,
)

# Input from user
setup_string = "First Measurement"
setup_ID1 = "id1"
setup_ID2 = "id2"
setup_test = 2  # ID of the pre-defined experiment setup

commands = [
    bytes([0x31]),  # COM Check
    bytes([0x30]) + setup_string.encode("ascii"),  # Set Identifiers “Title”
    bytes([0x38]) + setup_ID1.encode("ascii"),  # Set Identifiers “ID 1”
    bytes([0x39]) + setup_ID2.encode("ascii"),  # Set Identifiers “ID 2”
    bytes([0x36, setup_test]),
]

for command in commands:

    print(f"Sending command: {command}")
    ser.write(command)  # Send the command
    time.sleep(2)  # Wait a moment for the device to process the command

    # Check for and read the response from the host
    response = ser.read(1)

    # Convert response to string if any data is received
    if response:
        response_char = response.decode("ascii")  # Decode the response byte as ASCII

        # Check the response character
        if response_char == "K":
            print("Communication successful. Received 'K'.")
        elif response_char == "N":
            print("Invalid data request. Received 'N'.")
        else:
            print(f"Unexpected response received: {response_char}")
    else:
        print("No response received. Communication failed or timed out.")
