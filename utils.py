import time


def write_read(ser, x):
    # Send data to Arduino
    ser.write(bytes(x, "utf-8"))  # Send with newline

    # Wait for a response
    while True:
        data = ser.readline().decode("utf-8").strip()
        if data:  # Check if data is received
            return data
