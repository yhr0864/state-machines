import time
import logging
import serial

from transitions_gui import WebMachine

from utils import write_read


class TablePumpStateMachine:
    states = [
        "Empty_Empty",
        "Empty_BottleEmpty",
        # "Rotating",
        "BottleEmpty_Empty",
        "BottleFull_BottleEmpty",
        "BottleEmpty_BottleFull",
        "BottleFull_Empty",
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
    ]

    def __init__(self):
        self.ser = serial.Serial(port="COM8", baudrate=9600, timeout=0.1)

        # Initialize the state machine with shared state
        self.machine = WebMachine(
            model=self,
            states=TablePumpStateMachine.states,
            transitions=TablePumpStateMachine.transitions,
            initial="Empty_Empty",
            name="Rotational Table Pump",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        # Map states to corresponding transitions
        self.state_action_map = {
            "Empty_Empty": self.Tray_to_pump,
            "Empty_BottleEmpty": self.Rotate,
            "BottleEmpty_Empty": self.FillBottle_And_Tray_to_pump,
            "BottleFull_BottleEmpty": self.Rotate,
            "BottleEmpty_BottleFull": self.Pump_to_measure_And_FillBottle,
            "BottleFull_Empty": self.Tray_to_pump,
        }

        # Initialization
        logging.info("Homing the table")

        value = write_read(self.ser, "a")
        if value:
            logging.info(value)

    # Send command to gantry to implement Tray_to_pump
    def Tray_to_pump(self, sl):
        logging.info("Transitioning from tray to pump")
        # Send command
        sl[0] = "Tray_to_pump"
        # Receive feedback
        if sl[1] == "finishRequest":
            self.trigger("Tray_to_pump")

    # Send command to motor to implement Rotate
    def Rotate(self):
        logging.info("Rotating table")

        value = write_read(self.ser, "5")
        if value:
            logging.info(value)
            self.trigger("Rotate")

    # Send command to pump and gantry to simutaneously implement FillBottle_And_Tray_to_pump
    def FillBottle_And_Tray_to_pump(self):
        logging.info("Filling bottle and moving tray to pump")
        self.trigger("FillBottle_And_Tray_to_pump")

    def Pump_to_measure_And_FillBottle(self):
        logging.info("Pumping to measure and filling bottle")
        self.trigger("Pump_to_measure_And_FillBottle")

    def stop(self):
        logging.info("Stopping the process")
        self.trigger("stop")

    def auto_run(self, sl):
        """
        Automatically transitions through the states with a time delay.
        """
        while True:
            logging.info(f"Current state: {self.state}")
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
