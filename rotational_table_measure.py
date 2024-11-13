import time
import logging
import unittest
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


class TableMeasureStateMachine(unittest.TestCase):
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

    def __init__(self, shared_list, shared_dict, request_q):
        super().__init__()
        self.is_finished = shared_list
        self.request_q = request_q

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

        self.shared_state = shared_dict

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
        logging.info("Rotating Table_m")
        # logging.info(self.table_m_state)

        self.shared_state["table_m"] = state_rotate_120(self.shared_state["table_m"])
        self.trigger(self.shared_state["table_m"])

    def Pump_to_measure(self):
        logging.info("Table_m send command 'pump to measure' to gantry")

        # Send command
        self.request_q.put("Pump_to_measure")

        # Waiting until feedback received
        logging.info("Table_m waiting for Pump_to_measure")
        while True:
            # Check if Pump_to_measure finished
            if self.is_finished[1]:
                logging.info("Pump_to_measure finished")
                self.shared_state["table_p"], self.shared_state["table_m"] = (
                    state_pump_to_measure(
                        self.shared_state["table_p"], self.shared_state["table_m"]
                    )
                )
                self.trigger("Pump_to_measure_finished")

                # Reset list for next use
                self.is_finished[1] = False
                return
            time.sleep(0.1)

    def Pump_to_measure_and_UV(self):
        logging.info("Measuring with UV and moving from pump to measure")

        # Pump to measure and UV
        logging.info("Table_m send command 'pump to measure' to gantry and UV")
        # Send command
        self.request_q.put("Pump_to_measure")
        # Waiting until feedback received
        logging.info("Table_m waiting for Pump_to_measure and UV")
        while True:
            # Check if Pump_to_measure and UV finished
            if self.is_finished[1]:
                logging.info("Pump_to_measure and UV finished")
                self.shared_state["table_p"], self.shared_state["table_m"] = (
                    state_pump_to_measure_UV(
                        self.shared_state["table_p"], self.shared_state["table_m"]
                    )
                )

                # Testing if current state is correct
                self.assertEqual(self.shared_state["table_m"], "BottleM1_Empty_Bottle")
                self.trigger(self.shared_state["table_m"])

                # Reset list for next use
                self.is_finished[1] = False
                return
            time.sleep(0.1)

    def Pump_to_measure_and_UV_and_DLS(self):
        logging.info("Measuring with UV and DLS and moving from pump to measure")

        # Pump to measure and UV
        logging.info("Table_m send command 'pump to measure' to gantry and UV and DLS")
        # Send command
        self.request_q.put("Pump_to_measure")
        # Waiting until feedback received
        logging.info("Table_m waiting for Pump_to_measure and UV and DLS")
        while True:
            # Check if Pump_to_measure and UV and DLS finished
            if self.is_finished[1]:
                logging.info("Pump_to_measure and UV and DLS finished")
                self.shared_state["table_p"], self.shared_state["table_m"] = (
                    state_pump_to_measure_UV_DLS(
                        self.shared_state["table_p"], self.shared_state["table_m"]
                    )
                )

                # Testing if current state is correct
                self.assertEqual(
                    self.shared_state["table_m"], "BottleM1_BottleM2_Bottle"
                )
                self.trigger(self.shared_state["table_m"])

                # Reset list for next use
                self.is_finished[1] = False
                return
            time.sleep(0.1)

    def Measure_to_tray_and_UV_and_DLS(self):
        logging.info("Measuring with UV and DLS and moving from measure to tray")

        # Measure to tray and UV and DLS
        logging.info("Table_m send command 'measure to tray' to gantry and UV and DLS")
        # Send command
        self.request_q.put("Measure_to_tray")
        # Waiting until feedback received
        logging.info("Table_m waiting for Measure_to_tray and UV and DLS")
        while True:
            # Check if Measure_to_tray and UV and DLS finished
            if self.is_finished[2]:
                logging.info("Measure_to_tray and UV and DLS finished")
                self.shared_state["table_m"] = state_measure_to_tray_UV_DLS(
                    self.shared_state["table_m"]
                )

                # Testing if current state is correct
                self.assertEqual(
                    self.shared_state["table_m"], "BottleM1_BottleM2_Empty"
                )
                self.trigger(self.shared_state["table_m"])

                # Reset list for next use
                self.is_finished[2] = False
                return
            time.sleep(0.1)

    def start(self):
        if not self.running:
            self.running = True
            # logging.info("Starting the rotational table at measure.")
            self.trigger("Start")

    def stop(self):
        if self.running:
            self.running = False
            # logging.info("Stopping the process")
            self.trigger("Stop")

    def auto_run(self, queue):
        """
        Automatically transitions through the states with a time delay.
        """
        UI_inputs = {
            "0": self.start,
            "1": self.stop,
        }
        while True:
            # Check if there's any input in the queue: Start/Stop
            if not queue.empty():
                user_input = queue.get()
                if user_input in UI_inputs:
                    if user_input == "0":  # Start
                        while True:
                            if self.shared_state["table_m"].split("_")[-1] == "Bottle":
                                UI_inputs[user_input]()
                                break
                            time.sleep(0.1)
                    UI_inputs[user_input]()
                    # logging.info(
                    #     f"Received command {user_input}. Table_measure state: {self.state}"
                    # )
                else:
                    logging.warning(f"Invalid command: {user_input}")

            # Check if there's any command to implement
            else:
                if self.running:
                    logging.info(f"Current table_m state: {self.state}")
                    logging.info(f"Current table status: {self.shared_state}")
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
