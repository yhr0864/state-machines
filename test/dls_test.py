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


commands = [
    bytes([0x31]),  # COM Check
    # bytes([0x36, 2]),  # Select one pre-defined Measurement SOP
    # bytes([0x35]),  # Background Check
    # bytes([0x33]),  # Setzero (e.g. with water)
    # bytes([0x3A]),  # Sample Loading (with real sample)
    # bytes([0x34]),  # Run
    bytes([0x37, 1]),  # Request Data (Sample Loading)
    bytes([0x37, 2]),  # Request Data (Mean Volume Diameter (Mv))
    bytes([0x37, 3]),  # Request Data (Mean Area Diameter (Ma))
    bytes([0x37, 4]),  # Request Data (Mean Number Diameter (Mn))
    bytes([0x37, 5]),  # Request Data (Percentiles Values (s))
    bytes([0x37, 6]),  # Request Data (Size Percent Value(s))
    bytes([0x37, 7]),  # Request Data (Peaks Summary Value(s))
    bytes([0x37, 8]),  # Request Data (Tabular Data)
    bytes([0x37, 9]),  # Request Data (Zeta Potential)
]

for command in commands:

    print(f"Sending command: {command}")
    ser.write(command)  # Send the command
    time.sleep(2)  # Wait a moment for the device to process the command

    # Check for and read the response from the host
    response = ser.read(100)

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
