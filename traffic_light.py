import time
from transitions import Machine
from multiprocessing import shared_memory


class TrafficLight(object):

    states = ["green", "yellow", "red"]

    def __init__(self):
        # Initialize the state machine
        self.machine = Machine(model=self, states=TrafficLight.states, initial="green")

        self.machine.add_transition(trigger="timeup", source="green", dest="red")
        self.machine.add_transition("timeup", "red", "yellow")
        self.machine.add_transition("timeup", "yellow", "green")


if __name__ == "__main__":
    traffic_light = TrafficLight()

    max_state_length = max(len(state) for state in TrafficLight.states)
    data_size = max_state_length

    # Create shared memory with a custom name and size sufficient for the states
    shm = shared_memory.SharedMemory(name="my_custom_shm", create=True, size=data_size)

    try:
        while True:
            time.sleep(2)

            # Trigger state transition
            traffic_light.timeup()

            # Get the new state and encode it as bytes
            data = traffic_light.state
            data_bytes = data.encode("utf-8")

            # Zero out the buffer to prevent leftover data from previous writes
            shm.buf[:data_size] = b"\x00" * data_size

            # Write the new data to shared memory (only as many bytes as needed)
            shm.buf[: len(data_bytes)] = data_bytes

            # For debugging, print the current state
            print(f"Current state: {data}")

    except KeyboardInterrupt:
        pass
    finally:
        # Clean up shared memory when done
        shm.close()
        shm.unlink()
