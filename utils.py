import time


def write_read(ser, x):
    # Send data to Arduino
    ser.write(bytes(x, "utf-8"))  # Send with newline

    # Wait for a response
    while True:
        data = ser.readline().decode("utf-8").strip()
        if data:  # Check if data is received
            return data


def state_tray_to_pump(state):
    first, _ = state.split("_")
    return f"{first}_BottleEmpty"


def state_rotate(state):
    first, second = state.split("_")
    return f"{second}_{first}"


def state_rotate_120(state):
    first, second, third = state.split("_")
    return f"{third}_{first}_{second}"


def state_FillBottle_and_TraytoPump(state):
    state = "BottleFull_BottleEmpty"
    return state


def state_FillBottle_and_PumptoMeasure(state):
    state = "BottleFull_Empty"
    return state


def state_pump_to_measure(state):
    first, second, _ = state.split("_")
    return f"{first}_{second}_Bottle"


def state_pump_to_measure_UV(state):
    state = "BottleM1_Empty_Bottle"
    return state


def state_pump_to_measure_UV_DLS(state):
    state = "BottleM1_BottleM2_Bottle"
    return state


def state_measure_to_tray_UV_DLS(state):
    state = "BottleM1_BottleM2_Empty"
    return state
