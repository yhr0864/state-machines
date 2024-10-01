import time
import logging
from transitions_gui import WebMachine
from multiprocessing import Process, Queue, Manager

# Setup logging
logging.basicConfig(level=logging.INFO)


class TrafficLightStateMachine:
    states = ["green", "yellow", "red", "idle"]
    transitions = [
        {"trigger": "timeup", "source": "green", "dest": "yellow"},
        {"trigger": "timeup", "source": "yellow", "dest": "red"},
        {"trigger": "timeup", "source": "red", "dest": "green"},
        {"trigger": "stop", "source": ["red", "green", "yellow"], "dest": "idle"},
    ]

    def __init__(self):
        # Initialize the state machine
        self.machine = WebMachine(
            model=self,
            states=TrafficLightStateMachine.states,
            transitions=TrafficLightStateMachine.transitions,
            initial="red",
            name="Traffic Light",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            logging.info("Starting the traffic light.")
            self.trigger("timeup")  # Move to green state

    def stop(self):
        if self.running:
            self.running = False
            self.trigger("stop")  # Trigger transition to idle state
            logging.info("Stopping the traffic light. Moving to idle state.")

    def restore(self):
        if not self.running:
            self.start()  # Simply start the traffic light if it's not running
            logging.info(f"Restoring traffic light from state: {self.state}")

    def timeup(self):
        if self.running:
            self.trigger("timeup")


def auto_cycle(queue):
    traffic_light = TrafficLightStateMachine()
    commands = {
        "0": traffic_light.start,
        "1": traffic_light.stop,
        "2": traffic_light.restore,
    }

    while True:
        time.sleep(2)  # Simulate the time between state changes

        if not queue.empty():  # Check if there's any input in the queue
            user_input = queue.get()  # Get the input from the queue
            if user_input in commands:
                commands[user_input]()
                logging.info(
                    f"Received command {user_input}. Traffic light state: {traffic_light.state}"
                )
            else:
                logging.warning(f"Invalid command: {user_input}")
        else:
            if traffic_light.running:
                # If no input is received, and the machine is running, continue cycling through states
                traffic_light.timeup()
                logging.info(
                    f"Auto-cycling traffic light. Current state: {traffic_light.state}"
                )


def get_input(queue):
    while True:
        user_input = input("Enter command (0-start, 1-stop, 2-restore): ")
        queue.put(user_input)  # Put the input into the queue


if __name__ == "__main__":
    try:
        queue = Queue()  # Shared queue for communication

        # Start the background process (auto_cycle) that runs continuously
        p1 = Process(target=auto_cycle, args=(queue,))
        p1.start()

        # Handle input in the main process and send it to auto_cycle via the queue
        get_input(queue)

        p1.join()

    except KeyboardInterrupt:
        print("Stopping the processes...")
        p1.terminate()  # Gracefully stop the background process
        p1.join()  # Ensure process is terminated
