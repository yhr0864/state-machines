import time
import logging
import serial
import pickle

from transitions_gui import WebMachine

from utils import write_read


class TablePumpStateMachine:
    states = [
        "Empty_Empty",
        "Empty_BottleEmpty",
        "BottleEmpty_Empty",
        "BottleFull_BottleEmpty",
        "BottleEmpty_BottleFull",
        "BottleFull_Empty",
        "Idle",
    ]

    transitions = [
        {
            "trigger": "Tray_to_pump",
            "source": "Empty_Empty",
            "dest": "Empty_BottleEmpty",
        },
        {
            "trigger": "Rotate",
            "source": "Empty_BottleEmpty",
            "dest": "BottleEmpty_Empty",
            # "before": "Rotate_finished",
        },
        {
            "trigger": "FillBottle_And_Tray_to_pump",
            "source": "BottleEmpty_Empty",
            "dest": "BottleFull_BottleEmpty",
        },
        {
            "trigger": "Rotate",
            "source": "BottleFull_BottleEmpty",
            "dest": "BottleEmpty_BottleFull",
            # "after": "Rotate_finished",
        },
        {
            "trigger": "Pump_to_measure_And_FillBottle",
            "source": "BottleEmpty_BottleFull",
            "dest": "BottleFull_Empty",
        },
        {
            "trigger": "Tray_to_pump",
            "source": "BottleFull_Empty",
            "dest": "BottleFull_BottleEmpty",
        },
        {
            "trigger": "Start",
            "source": "Idle",
            "dest": "Empty_Empty",
        },
        {
            "trigger": "Stop",
            "source": [
                "Empty_Empty",
                "Empty_BottleEmpty",
                "BottleEmpty_Empty",
                "BottleFull_BottleEmpty",
                "BottleEmpty_BottleFull",
                "BottleFull_Empty",
            ],
            "dest": "Idle",
        },
    ]

    def __init__(self, shared_list):
        # self.ser = serial.Serial(port="COM8", baudrate=9600, timeout=0.1)
        self.shared_list = shared_list

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

        self.dump = None
        self.running = False

        # Map states to corresponding transitions
        self.state_action_map = {
            "Idle": self.start,
            "Empty_Empty": self.Tray_to_pump,
            "Empty_BottleEmpty": self.Rotate,
            "BottleEmpty_Empty": self.FillBottle_And_Tray_to_pump,
            "BottleFull_BottleEmpty": self.Rotate,
            "BottleEmpty_BottleFull": self.Pump_to_measure_And_FillBottle,
            "BottleFull_Empty": self.Tray_to_pump,
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
        self.shared_list[0] = "Tray_to_pump"

        # Waiting until feedback received
        logging.info("Waiting for Tray_to_pump")
        while True:
            if self.shared_list[1] == "finishRequest":
                logging.info("Tray_to_pump finished")
                self.trigger("Tray_to_pump")

                # Reset list for next use
                self.shared_list[1] = "waiting for feedback"
                return

    # Send command to motor to implement Rotate
    def Rotate(self):
        logging.info("Rotating table")

        # value = write_read(self.ser, "5")
        # if value:
        # logging.info(value)
        self.trigger("Rotate")

    # Send command to pump and gantry to simutaneously implement FillBottle_And_Tray_to_pump
    def FillBottle_And_Tray_to_pump(self):
        logging.info("Filling bottle and moving tray to pump")
        self.trigger("FillBottle_And_Tray_to_pump")

    def Pump_to_measure_And_FillBottle(self):
        logging.info("Pumping to measure and filling bottle")
        self.trigger("Pump_to_measure_And_FillBottle")

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
        commands = {
            "0": self.start,
            "1": self.stop,
            "2": self.restore,
        }
        while True:
            if not queue.empty():  # Check if there's any input in the queue
                user_input = queue.get()  # Get the input from the queue
                if user_input in commands:
                    commands[user_input]()
                    logging.info(
                        f"Received command {user_input}. Table_pump state: {self.state}"
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

                    time.sleep(3)  # Delay between state transitions


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
