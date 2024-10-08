import time
import logging
from transitions_gui import WebMachine

from utils import (
    state_rotate_120,
    state_pump_to_measure,
    state_pump_to_measure_UV,
    state_pump_to_measure_UV_DLS,
    state_measure_to_tray_UV_DLS,
)

# Setup logging
logging.basicConfig(level=logging.INFO)


class TableMeasureStateMachine:
    states = [
        "Pump_to_measure",
        "Rotating",
        "Pump_to_measure_and_UV",
        "Pump_to_measure_and_UV_and_DLS",
        "Measure_to_tray_and_UV_and_DLS",
        "Idle",
    ]

    transitions = [
        {
            "trigger": "Start",
            "source": "Idle",
            "dest": "Pump_to_measure",
        },
        {
            "trigger": "Pump_to_measure_finished",
            "source": "Pump_to_measure",
            "dest": "Rotating",
        },
        {
            "trigger": "Bottle_Empty_Empty",
            "source": "Rotating",
            "dest": "Pump_to_measure_and_UV",
        },
        {
            "trigger": "BottleM1_Empty_Bottle",
            "source": "Pump_to_measure_and_UV",
            "dest": "Rotating",
        },
        {
            "trigger": "Bottle_BottleM1_Empty",
            "source": "Rotating",
            "dest": "Pump_to_measure_and_UV_and_DLS",
        },
        {
            "trigger": "BottleM1_BottleM2_Bottle",
            "source": "Pump_to_measure_and_UV_and_DLS",
            "dest": "Rotating",
        },
        {
            "trigger": "Bottle_BottleM1_BottleM2",
            "source": "Rotating",
            "dest": "Measure_to_tray_and_UV_and_DLS",
        },
        {
            "trigger": "BottleM1_BottleM2_Empty",
            "source": "Measure_to_tray_and_UV_and_DLS",
            "dest": "Pump_to_measure",
        },
        {
            "trigger": "Stop",
            "source": [
                "Pump_to_measure",
                "Rotating",
                "Pump_to_measure_and_UV",
                "Pump_to_measure_and_UV_and_DLS",
                "Measure_to_tray_and_UV_and_DLS",
            ],
            "dest": "Idle",
        },
    ]

    def __init__(self, shared_list):
        # self.shared_list = shared_list

        # Initialize the state machine with shared state
        self.machine = WebMachine(
            model=self,
            states=TableMeasureStateMachine.states,
            transitions=TableMeasureStateMachine.transitions,
            initial="Idle",
            name="Table Measure",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8085,
        )

        self.table_state = "Empty_Empty_Empty"
        self.running = False

        # Map states to corresponding transitions
        self.state_action_map = {
            "Idle": self.start,
            "Pump_to_measure": self.Pump_to_measure,
            "Rotating": self.Rotate,
            "Pump_to_measure_and_UV": self.Pump_to_measure_and_UV,
            "Pump_to_measure_and_UV_and_DLS": self.Pump_to_measure_and_UV_and_DLS,
            "Measure_to_tray_and_UV_and_DLS": self.Measure_to_tray_and_UV_and_DLS,
        }

    def Rotate(self):
        logging.info("Rotating table")
        logging.info(self.table_state)

        self.table_state = state_rotate_120(self.table_state)
        self.trigger(self.table_state)

    def Pump_to_measure(self):
        logging.info("Send command 'pump to measure' to gantry")

        # Send command
        # self.shared_list[0] = "Pump_to_measure"

        # Waiting until feedback received
        logging.info("Waiting for Pump_to_measure")
        # while True:
        #     if self.shared_list[1] == "finishRequest":
        logging.info("Pump_to_measure finished")
        self.table_state = state_pump_to_measure(self.table_state)
        self.trigger("Pump_to_measure_finished")

        # Reset list for next use
        # self.shared_list[1] = "waiting for feedback"
        return

    def Pump_to_measure_and_UV(self):
        logging.info("Measuring with UV and moving from pump to measure")

        self.table_state = state_pump_to_measure_UV(self.table_state)
        self.trigger(self.table_state)

    def Pump_to_measure_and_UV_and_DLS(self):
        logging.info("Measuring with UV and DLS and moving from pump to measure")

        self.table_state = state_pump_to_measure_UV_DLS(self.table_state)
        self.trigger(self.table_state)

    def Measure_to_tray_and_UV_and_DLS(self):
        logging.info("Measuring with UV and DLS and moving from measure to tray")

        self.table_state = state_measure_to_tray_UV_DLS(self.table_state)
        self.trigger(self.table_state)

    def start(self):
        if not self.running:
            self.running = True
            logging.info("Starting the rotational table at measure.")
            self.trigger("Start")

    def stop(self):
        if self.running:
            self.running = False
            logging.info("Stopping the process")
            self.trigger("Stop")

    def auto_run(self, queue):
        """
        Automatically transitions through the states with a time delay.
        """
        commands = {
            "0": self.start,
            "1": self.stop,
        }
        while True:
            if not queue.empty():  # Check if there's any input in the queue
                user_input = queue.get()  # Get the input from the queue
                if user_input in commands:
                    commands[user_input]()
                    logging.info(
                        f"Received command {user_input}. Table_measure state: {self.state}"
                    )
                else:
                    logging.warning(f"Invalid command: {user_input}")

            else:
                if self.running:
                    logging.info(f"Current table state: {self.state}")
                    action = self.state_action_map.get(self.state)

                    if action:
                        action()  # Call the action associated with the current state
                    else:
                        logging.error(f"No action defined for state: {self.state}")

                    time.sleep(2)  # Delay between state transitions


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create the table state machine
    table = TableMeasureStateMachine()

    try:
        # Start automatic state transitions
        table.auto_run()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()

    # # Create the table state machine
    # table = TableMeasureStateMachine()

    # # Mapping user inputs to the respective state machine actions
    # actions = {
    #     0: table.stop,
    #     1: table.Pump_to_measure,
    #     2: table.Rotate,
    #     3: table.UV_Measure_And_Pump_to_measure,
    #     4: table.Pump_to_measure_And_UV_measure_And_DLS_measure,
    #     5: table.Measure_to_tray_And_UV_measure_And_DLS_measure,
    # }

    # try:
    #     while True:
    #         # Display the options for user input
    #         next_action = int(
    #             input(
    #                 "Please select the next command:\n"
    #                 "0-stop; 1-pump_to_measure; 2-rotate; "
    #                 "3-UV_Measure_And_Pump_to_measure; "
    #                 "4-Pump_to_measure_And_UV_measure_And_DLS_measure; "
    #                 "5-Measure_to_tray_And_UV_measure_And_DLS_measure; "
    #             )
    #         )

    #         # Trigger the corresponding action
    #         if next_action in actions:
    #             actions[next_action]()  # Call the appropriate method based on input
    #             logging.info(f"Table state: {table.state}")
    #         else:
    #             logging.error("Invalid input! Please select a valid command.")

    # except KeyboardInterrupt:
    #     logging.info("Stopping the server...")
    #     table.machine.stop_server()
