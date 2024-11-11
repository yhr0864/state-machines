import time
import logging
import serial
import pickle

from transitions_gui import WebMachine

from utils import (
    write_read,
    state_rotate,
    state_tray_to_pump,
    state_pump_to_measure,
    state_FillBottle_and_TraytoPump,
    state_FillBottle_and_PumptoMeasure,
)


class TablePumpStateMachine:
    states = [
        "Tray_to_pump",
        "Rotating",
        "FillBottle_and_TraytoPump",
        "FillBottle_and_PumptoMeasure",
        "Idle",
    ]

    transitions = [
        {
            "trigger": "Start",
            "source": "Idle",
            "dest": "Tray_to_pump",
        },
        {
            "trigger": "Tray_to_pump_finished",
            "source": "Tray_to_pump",
            "dest": "Rotating",
        },
        {
            "trigger": "BottleEmpty_Empty",
            "source": "Rotating",
            "dest": "FillBottle_and_TraytoPump",
        },
        {
            "trigger": "BottleFull_BottleEmpty",
            "source": "FillBottle_and_TraytoPump",
            "dest": "Rotating",
        },
        {
            "trigger": "BottleEmpty_BottleFull",
            "source": "Rotating",
            "dest": "FillBottle_and_PumptoMeasure",
        },
        {
            "trigger": "BottleFull_Empty",
            "source": "FillBottle_and_PumptoMeasure",
            "dest": "Tray_to_pump",
        },
        {
            "trigger": "Stop",
            "source": [
                "Tray_to_pump",
                "Rotating",
                "FillBottle_and_TraytoPump",
                "FillBottle_and_PumptoMeasure",
            ],
            "dest": "Idle",
        },
    ]

    def __init__(self, shared_list, shared_dict, request_q):
        # self.ser = serial.Serial(port="COM8", baudrate=9600, timeout=0.1)
        self.is_finished = shared_list
        self.request_q = request_q

        # Initialize the state machine with shared state
        self.machine = WebMachine(
            model=self,
            states=TablePumpStateMachine.states,
            transitions=TablePumpStateMachine.transitions,
            initial="Idle",
            name="Table Pump",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.shared_state = shared_dict

        self.dump = None
        self.running = False

        # Map states to corresponding transitions
        self.state_action_map = {
            "Idle": self.start,
            "Tray_to_pump": self.Tray_to_pump,
            "Rotating": self.Rotate,
            "FillBottle_and_TraytoPump": self.FillBottle_and_TraytoPump,
            "FillBottle_and_PumptoMeasure": self.FillBottle_and_PumptoMeasure,
            # "Idle": self.restore,
        }

        # Initialization
        # logging.info("Homing the table")

        # value = write_read(self.ser, "a")
        # if value:
        #     logging.info(value)

    # Send command to gantry to implement Tray_to_pump
    def Tray_to_pump(self):
        logging.info("Table_p send command 'tray to pump' to gantry")

        # Send command
        self.request_q.put("Tray_to_pump")

        # Waiting until feedback received
        logging.info("Table_p waiting for Tray_to_pump")
        while True:
            # Check if Tray_to_pump finished
            if self.is_finished[0]:
                logging.info("Tray_to_pump finished")
                self.shared_state["table_p"] = state_tray_to_pump(
                    self.shared_state["table_p"]
                )
                self.trigger("Tray_to_pump_finished")

                # Reset list for next use
                self.is_finished[0] = False
                return
            time.sleep(0.1)

    # Send command to motor to implement Rotate
    def Rotate(self):
        logging.info("Rotating table_p")

        # value = write_read(self.ser, "5")
        # if value:
        # logging.info(value)
        self.shared_state["table_p"] = state_rotate(self.shared_state["table_p"])
        self.trigger(self.shared_state["table_p"])

    # Send command to pump and gantry to simutaneously implement FillBottle_And_Tray_to_pump
    def FillBottle_and_TraytoPump(self):
        logging.info("Filling bottle and moving tray to pump")

        # Tray to pump
        logging.info("Table_p send command 'tray to pump' to gantry and filling")
        # Send command
        self.request_q.put("Tray_to_pump")
        # Waiting until feedback received
        logging.info("Table_p waiting for Tray_to_pump and filling")
        while True:
            # Check if Tray_to_pump finished
            if self.is_finished[0]:
                logging.info("Tray_to_pump and filling finished")
                # Here we need to call pump() as well
                # Make sure pump finished!!!
                self.shared_state["table_p"] = state_FillBottle_and_TraytoPump(
                    self.shared_state["table_p"]
                )
                self.trigger(self.shared_state["table_p"])

                # Reset list for next use
                self.is_finished[0] = False
                return
            time.sleep(0.1)

    def FillBottle_and_PumptoMeasure(self):
        logging.info("Pumping to measure and filling bottle")

        # Pump to measure
        logging.info("Table_p send command 'pump to measure' to gantry and filling")
        # Send command
        self.request_q.put("Pump_to_measure")
        # Waiting until feedback received
        logging.info("Table_p waiting for Pump_to_measure and filling")
        while True:
            # Check if Tray_to_pump finished
            if self.is_finished[1]:
                logging.info("Pump_to_measure and filling finished")
                # Here we need to call pump() as well
                # Make sure pump finished!!!
                self.shared_state["table_p"], self.shared_state["table_m"] = (
                    state_FillBottle_and_PumptoMeasure(
                        self.shared_state["table_p"], self.shared_state["table_m"]
                    )
                )
                self.trigger(self.shared_state["table_p"])

                # Reset list for next use
                self.is_finished[1] = False
                return
            time.sleep(0.1)

    def start(self):
        if not self.running:
            self.running = True
            logging.info("Starting the rotational table at pump.")
            self.trigger("Start")

    def stop(self):
        if self.running:
            self.running = False
            logging.info("Stopping the process")
            # self.store()
            self.trigger("Stop")

    def store(self):
        self.dump = pickle.dumps(self.machine)

    def restore(self):
        self.dump = pickle.loads(self.dump)
        logging.info(f"Restoring the state: {self.dump.state}")
        self.trigger(self.dump.state)

    def auto_run(self, queue):
        """
        Automatically transitions through the states with a time delay.
        """
        UI_inputs = {
            "0": self.start,
            "1": self.stop,
            "2": self.restore,
        }
        while True:
            # Check if there's any input in the queue: Start/Stop
            if not queue.empty():
                user_input = queue.get()
                if user_input in UI_inputs:
                    UI_inputs[user_input]()
                    logging.info(
                        f"Received command {user_input}. Table_pump state: {self.state}"
                    )
                else:
                    logging.warning(f"Invalid command: {user_input}")

            # Check if there's any command to implement
            else:
                if self.running:
                    logging.info(f"Current table_p state: {self.state}")
                    action = self.state_action_map.get(self.state)

                    if action:
                        action()
                    else:
                        logging.error(f"No action defined for state: {self.state}")

                    time.sleep(2)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create the table state machine
    table = TablePumpStateMachine()

    try:
        # Start automatic state transitions
        table.auto_run()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()
