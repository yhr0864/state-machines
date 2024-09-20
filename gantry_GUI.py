import time
import logging
from transitions_gui import WebMachine

# Setup logging
logging.basicConfig(level=logging.INFO)


class GantryStateMachine:
    states = ["idle", "tray_to_pump", "pump_to_measure", "measure_to_tray"]
    transitions = [
        ["event_1", "idle", "tray_to_pump"],
        ["event_2", "tray_to_pump", "pump_to_measure"],
        ["event_3", "pump_to_measure", "measure_to_tray"],
        ["event_4", "measure_to_tray", "tray_to_pump"],
        ["stop", "*", "idle"],
    ]

    def __init__(self):
        # Initialize the state machine
        self.machine = WebMachine(
            model=self,
            states=GantryStateMachine.states,
            transitions=GantryStateMachine.transitions,
            initial="idle",
            name="Gantry",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

    # Transition methods for triggering events
    def stop(self):
        logging.info("Gantry stopping...")
        self.machine.stop()

    def event_1(self):
        logging.info("Transitioning from idle to tray_to_pump")
        self.machine.trigger("event_1")

    def event_2(self):
        logging.info("Transitioning from tray_to_pump to pump_to_measure")
        self.machine.trigger("event_2")

    def event_3(self):
        logging.info("Transitioning from pump_to_measure to measure_to_tray")
        self.machine.trigger("event_3")

    def event_4(self):
        logging.info("Transitioning from measure_to_tray to tray_to_pump")
        self.machine.trigger("event_4")


if __name__ == "__main__":
    # Create the gantry state machine
    gantry = GantryStateMachine()

    # Mapping user inputs to the respective state machine actions
    actions = {
        0: gantry.stop,
        1: gantry.event_1,
        2: gantry.event_2,
        3: gantry.event_3,
        4: gantry.event_4,
    }

    try:
        while True:
            # Display the options for user input
            next_action = int(
                input(
                    "Please select the next command: 0-stop; 1-tray_to_pump; 2-pump_to_measure; 3-measure_to_tray; 4-loop_back_to_tray_to_pump: "
                )
            )

            # Trigger the corresponding action
            if next_action in actions:
                actions[next_action]()  # Call the appropriate method based on input
                logging.info(f"Gantry state: {gantry.state}")
            else:
                logging.error("Invalid input! Please select a valid command.")

    except KeyboardInterrupt:  # Ctrl + C to stop the server
        logging.info("Stopping the server...")
        gantry.machine.stop_server()
