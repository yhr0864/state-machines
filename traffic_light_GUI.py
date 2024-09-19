import time
import logging

from transitions_gui import WebMachine
from multiprocessing import shared_memory

# Setup logging
logging.basicConfig(level=logging.INFO)


class TrafficLightStateMachine:
    states = ["green", "yellow", "red"]

    def __init__(self):
        # Initialize the state machine
        self.machine = WebMachine(
            model=self,
            states=TrafficLightStateMachine.states,
            initial="red",
            name="Traffic Light",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.machine.add_transition(trigger="timeup", source="green", dest="yellow")
        self.machine.add_transition(trigger="timeup", source="yellow", dest="red")
        self.machine.add_transition(trigger="timeup", source="red", dest="green")


if __name__ == "__main__":
    # Create the traffic light state machine
    traffic_light = TrafficLightStateMachine()

    max_state_length = max(len(state) for state in traffic_light.states)
    data_size = max_state_length

    # Create shared memory with a custom name and size sufficient for the states
    shm = shared_memory.SharedMemory(name="my_custom_shm", create=True, size=data_size)

    # Main loop to change states
    try:
        while True:
            time.sleep(2)

            traffic_light.timeup()

            # Get the new state and encode it as bytes
            data = traffic_light.state
            data_bytes = data.encode("utf-8")

            # Zero out the buffer to prevent leftover data from previous writes
            shm.buf[:data_size] = b"\x00" * data_size

            # Write the new data to shared memory (only as many bytes as needed)
            shm.buf[: len(data_bytes)] = data_bytes

            logging.info(f"Traffic light state: {traffic_light.state}")

    except KeyboardInterrupt:  # Ctrl + C to stop the server
        traffic_light.machine.stop_server()

    finally:
        # Clean up shared memory when done
        shm.close()
        shm.unlink()
