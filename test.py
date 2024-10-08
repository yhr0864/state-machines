import time
import logging
import serial
import pickle

from transitions_gui import WebMachine

from utils import (
    write_read,
    state_rotate,
    state_pump_to_tray,
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

    def __init__(self):
        # self.ser = serial.Serial(port="COM8", baudrate=9600, timeout=0.1)
        # self.shared_list = shared_list

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

        self.table_state = "Empty_Empty"
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
        logging.info("Send command 'tray to pump' to gantry")
        # Send command
        # self.shared_list[0] = "Tray_to_pump"

        # Waiting until feedback received
        logging.info("Waiting for Tray_to_pump")
        # while True:
        #     if self.shared_list[1] == "finishRequest":
        logging.info("Tray_to_pump finished")
        time.sleep(2)
        self.table_state = state_pump_to_tray(self.table_state)
        self.trigger("Tray_to_pump_finished")

        # # Reset list for next use
        # self.shared_list[1] = "waiting for feedback"
        # return

    # Send command to motor to implement Rotate
    def Rotate(self):
        logging.info("Rotating table")

        # value = write_read(self.ser, "5")
        # if value:
        # logging.info(value)
        self.table_state = state_rotate(self.table_state)
        self.trigger(self.table_state)

    # Send command to pump and gantry to simutaneously implement FillBottle_And_Tray_to_pump
    def FillBottle_and_TraytoPump(self):
        logging.info("Filling bottle and moving tray to pump")
        self.table_state = state_FillBottle_and_TraytoPump(self.table_state)
        self.trigger(self.table_state)

    def FillBottle_and_PumptoMeasure(self):
        logging.info("Pumping to measure and filling bottle")
        self.table_state = state_FillBottle_and_PumptoMeasure(self.table_state)
        self.trigger(self.table_state)

    def start(self):
        # if not self.running:
        #     self.running = True
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

    def auto_run(self):
        """
        Automatically transitions through the states with a time delay.
        """
        while True:

            logging.info(f"Current table state: {self.state}")
            action = self.state_action_map.get(self.state)

            if action:
                action()  # Call the action associated with the current state
            else:
                logging.error(f"No action defined for state: {self.state}")

            time.sleep(1)  # Delay between state transitions


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
