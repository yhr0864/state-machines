import time
import logging
from transitions_gui import WebMachine


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
        {
            "trigger": "stop",
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
        self.running = False

        self.state_action_map = {
            "Tray_to_pump": self.getRequest_Tray_to_pump,
            "Measure_to_tray": self.getRequest_Measure_to_tray,
            "Pump_to_measure": self.getRequest_Pump_to_measure,
        }

    def start(self):
        if not self.running:
            self.running = True
            logging.info("Starting the gantry.")

    # Transition methods for triggering events
    def stop(self):
        if self.running:
            self.running = False
            self.trigger("stop")  # Trigger transition to idle state
            logging.info("Gantry stopping...")

    def getRequest_Tray_to_pump(self):
        logging.info("Get request, transitioning from Idle to Tray_to_pump")
        self.trigger("getRequest_Tray_to_pump")
        # Simulate finishing the request
        time.sleep(3)  # Simulate some processing time
        self.finishRequest(0)

    def getRequest_Measure_to_tray(self):
        logging.info("Get request, transitioning from Idle to Measure_to_tray")
        self.trigger("getRequest_Measure_to_tray")
        # Simulate finishing the request
        time.sleep(3)  # Simulate some processing time
        self.finishRequest(2)

    def getRequest_Pump_to_measure(self):
        logging.info("Get request, transitioning from Idle to Pump_to_measure")
        self.trigger("getRequest_Pump_to_measure")
        # Simulate finishing the request
        time.sleep(3)  # Simulate some processing time
        self.finishRequest(1)

    def finishRequest(self, list_index):
        # Automatically return to idle state after a request is finished
        logging.info("Gantry: Returning to Idle state automatically")
        time.sleep(1)

        # Reset shared list
        self.shared_list[list_index] = True

        self.trigger("finishRequest")
        logging.info(f"Gantry state after auto return: {self.state}")

    def auto_run(self, queue, request_q):

        input_commands = {
            "0": self.start,
            "1": self.stop,
        }
        while True:
            if not queue.empty():  # Check if there's any input in the queue
                user_input = queue.get()  # Get the input from the queue
                if user_input in input_commands:
                    input_commands[user_input]()
                    logging.info(
                        f"Received user command {user_input}. Gantry state: {self.state}"
                    )
                else:
                    logging.warning(f"Invalid command: {user_input}")
            else:
                if self.running:
                    if not request_q.empty():
                        request = request_q.get()  # Get the request from the queue
                        action = self.state_action_map.get(request)

                        if action:
                            action()
                        else:
                            logging.error(f"No action defined for request: {request}")

                        time.sleep(2)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

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
