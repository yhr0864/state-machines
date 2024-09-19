import time
import logging
from transitions import Machine
from transitions_gui import WebMachine

# Setup logging
logging.basicConfig(level=logging.INFO)


# Define Traffic Light State Machine
class TrafficLightStateMachine(object):
    states = ["green", "yellow", "red"]

    def __init__(self):
        # Initialize the state machine
        self.machine = WebMachine(
            model=self,
            states=TrafficLightStateMachine.states,
            initial="red",
            name="Traffic Light",
            ordered_transitions=True,
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.machine.add_transition(trigger="timeup", source="green", dest="yellow")
        self.machine.add_transition(trigger="timeup", source="yellow", dest="red")
        self.machine.add_transition(trigger="timeup", source="red", dest="green")

    # def timeup(self):
    #     # Transition to the next state and update the shared memory
    #     self.trigger("timeup")


# Create the traffic light state machine
traffic_light = TrafficLightStateMachine()


# Main loop to change states
try:
    while True:
        time.sleep(2)  # Wait for 2 seconds
        traffic_light.next_state()  # Trigger the state transition
        logging.info(
            f"Traffic light state: {traffic_light.state}"
        )  # Log the current state
except KeyboardInterrupt:  # Ctrl + C to stop the server
    traffic_light.stop_server()
