import time


def write_read(ser, x):
    # Send data to Arduino
    ser.write(bytes(x, "utf-8"))  # Send with newline

    # Wait for a response
    while True:
        data = ser.readline().decode("utf-8").strip()
        if data:  # Check if data is received
            return data


def state_tray_to_pump(state: str):
    first, _ = state.split("_")
    return f"{first}_BottleEmpty"


def state_rotate(state: str):
    first, second = state.split("_")
    return f"{second}_{first}"


def state_rotate_120(state: str):
    first, second, third = state.split("_")
    return f"{third}_{first}_{second}"


def state_FillBottle_and_TraytoPump(state: str):
    state = "BottleFull_BottleEmpty"
    return state


def state_FillBottle_and_PumptoMeasure(state_p, state_m):
    state_p = "BottleFull_Empty"
    _, state_m = state_pump_to_measure(state_p, state_m)
    return state_p, state_m


def state_pump_to_measure(state_p, state_m):
    first_p, _ = state_p.split("_")
    first_m, second_m, _ = state_m.split("_")
    state_p = f"{first_p}_Empty"
    state_m = f"{first_m}_{second_m}_Bottle"
    return state_p, state_m


def state_pump_to_measure_UV(state_p, state_m):
    state_p, _ = state_pump_to_measure(state_p, state_m)
    state_m = "BottleM1_Empty_Bottle"
    return state_p, state_m


def state_pump_to_measure_UV_DLS(state_p, state_m):
    state_p, _ = state_pump_to_measure(state_p, state_m)
    state_m = "BottleM1_BottleM2_Bottle"
    return state_p, state_m


def state_measure_to_tray_UV_DLS(state: str):
    state = "BottleM1_BottleM2_Empty"
    return state
