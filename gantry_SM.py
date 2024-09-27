import time
import logging
from transitions_gui import WebMachine

# Setup logging
logging.basicConfig(level=logging.INFO)


class GantryStateMachine:
    states = ["Idle", "Tray_to_pump", "Pump_to_measure", "Measure_to_tray"]
    transitions = [
        {
            "trigger": "getRequest_Tray_to_pump",
            "source": "Idle",
            "dest": "Tray_to_pump",
        },
        {
            "trigger": "getRequest_Measure_to_tray",
            "source": "Idle",
            "dest": "Measure_to_tray",
        },
        {
            "trigger": "getRequest_Pump_to_measure",
            "source": "Idle",
            "dest": "Pump_to_measure",
        },
        {
            "trigger": "finishRequest",
            "source": ["Tray_to_pump", "Measure_to_tray", "Pump_to_measure"],
            "dest": "Idle",
        },
    ]

    def __init__(self, shared_list):
        self.shared_list = shared_list
        # Initialize the state machine
        self.machine = WebMachine(
            model=self,
            states=GantryStateMachine.states,
            transitions=GantryStateMachine.transitions,
            initial="Idle",
            name="Gantry",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8084,
        )

    # @property
    # def state(self):
    #     # Return the state from the shared memory
    #     return self.shared_state.value

    # @state.setter
    # def state(self, value):
    #     # Update the state in the shared memory
    #     self.shared_state.value = value

    # Transition methods for triggering events
    def stop(self):
        logging.info("Gantry stopping...")

    def getRequest_Tray_to_pump(self):
        logging.info("Get request, transitioning from Idle to Tray_to_pump")
        self.trigger("getRequest_Tray_to_pump")
        # Simulate finishing the request
        time.sleep(10)  # Simulate some processing time
        self.finishRequest()

    def getRequest_Measure_to_tray(self):
        logging.info("Processing request 2, transitioning from Idle to Measure_to_tray")
        self.trigger("getRequest_Measure_to_tray")
        # Simulate finishing the request
        time.sleep(1)  # Simulate some processing time
        self.finishRequest()

    def getRequest_Pump_to_measure(self):
        logging.info("Processing request 3, transitioning from Idle to Pump_to_measure")
        self.trigger("getRequest_Pump_to_measure")
        # Simulate finishing the request
        time.sleep(1)  # Simulate some processing time
        self.finishRequest()

    def finishRequest(self):
        # Automatically return to idle state after a request is finished
        logging.info("Gantry: Returning to Idle state automatically")
        time.sleep(1)

        self.shared_list[0] = "waiting for command"
        self.shared_list[1] = "finishRequest"

        self.trigger("finishRequest")
        logging.info(f"Gantry state after auto return: {self.state}")


if __name__ == "__main__":
    # Create the gantry state machine
    gantry = GantryStateMachine()

    # Mapping user inputs to the respective state machine actions
    actions = {
        0: gantry.stop,
        1: gantry.getRequest_Tray_to_pump,
        2: gantry.getRequest_Measure_to_tray,
        3: gantry.getRequest_Pump_to_measure,
    }

    try:
        while True:
            # Display the options for user input
            next_action = int(
                input(
                    "Please select the next command: 0-stop; 1-getRequest1; 2-getRequest2; 3-getRequest3: "
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
