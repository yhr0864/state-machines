import time
from transitions import Machine
from multiprocessing import shared_memory


class Vehicle:
    states = ["stop", "moving"]

    def __init__(self):
        # Initialize the state machine for the vehicle
        self.machine = Machine(model=self, states=Vehicle.states, initial="stop")

        self.machine.add_transition("start_engine", "stop", "moving")
        self.machine.add_transition("brake", "moving", "stop")

    def handle_traffic_light(self, traffic_light_state):
        # This is the switcher pattern integrated into the vehicle class
        method_name = "handle_" + str(traffic_light_state)
        method = getattr(self, method_name, lambda: "No action for this state")
        return method()

    def handle_red(self):
        if self.state == "moving":
            self.brake()
            return "Car stops"
        else:
            return "Car is already stopped"

    def handle_green(self):
        if self.state == "stop":
            self.start_engine()
            return "Car moves"
        else:
            return "Car is already moving"

    def handle_yellow(self):
        # Yellow could be handled with a default message or another action
        return "Car is waiting..."


if __name__ == "__main__":
    car = Vehicle()

    # Connect to the existing shared memory block using the known name
    shm_name = "my_custom_shm"
    existing_shm = shared_memory.SharedMemory(name=shm_name)

    # Define the size based on the longest possible traffic light state (green, yellow, red)
    data_size = 6  # "yellow" is the longest state with 6 characters

    try:
        while True:
            time.sleep(1)

            # Read the byte data from shared memory
            data_bytes = bytes(existing_shm.buf[:data_size])

            # Convert the bytes back into a string and remove null bytes
            data = data_bytes.decode("utf-8").rstrip("\x00")
            print(f"Now is {data}")

            # Transition based on the traffic light state
            action_result = car.handle_traffic_light(data)

            if action_result:
                print(action_result)

    except KeyboardInterrupt:
        pass

    finally:
        # Clean up shared memory
        existing_shm.close()
