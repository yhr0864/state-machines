import time
import logging
from transitions import Machine
from transitions_gui import WebMachine  # Ensure this is installed

# Setup logging
logging.basicConfig(level=logging.INFO)


# Define Traffic Light State Machine
class TrafficLightStateMachine(object):
    states = ["green", "yellow", "red"]
    transitions = [
        ["timeup", "red", "green"],
        ["timeup", "green", "yellow"],
        ["timeup", "yellow", "red"],
    ]

    def __init__(self):
        # Initialize the state machine
        self.machine = Machine(
            model=self, states=TrafficLightStateMachine.states, initial="green"
        )

        self.machine.add_transition(trigger="timeup", source="green", dest="yellow")
        self.machine.add_transition(trigger="timeup", source="yellow", dest="red")
        self.machine.add_transition(trigger="timeup", source="red", dest="green")


# Create the traffic light state machine
traffic_light = TrafficLightStateMachine()


# Set up the WebMachine for visualization
states = traffic_light.states
web_machine = WebMachine(
    states=states,
    initial=traffic_light.state,
    # transitions=traffic_light.transitions,
    name="Traffic Light",
    ordered_transitions=True,
    ignore_invalid_triggers=True,
    auto_transitions=False,
    port=8083,
)

# states = ["A", "B", "C", "D", "E", "F"]
# web_machine = WebMachine(
#     states=states,
#     initial=states[0],
#     name="Traffic Light",
#     ordered_transitions=True,
#     ignore_invalid_triggers=True,
#     auto_transitions=False,
#     port=8083,
# )

# Main loop to change states
try:
    while True:
        time.sleep(2)  # Wait for 2 seconds
        web_machine.next_state()  # Trigger the state transition
        logging.info(
            f"Traffic light state: {traffic_light.state}"
        )  # Log the current state
except KeyboardInterrupt:  # Ctrl + C to stop the server
    web_machine.stop_server()
