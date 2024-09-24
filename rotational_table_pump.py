import time
import logging
from transitions_gui import WebMachine
from multiprocessing import Process, Manager

# Setup logging
logging.basicConfig(level=logging.INFO)


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
        # {
        #     "trigger": "Rotate_finished",
        #     "source": "Rotating",
        #     "dest": "BottleEmpty_BottleFull",
        #     # "before": "Rotate_finished",
        # },
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

    def Tray_to_pump(self):
        logging.info("Transitioning from tray to pump")
        self.trigger("Tray_to_pump")

    def Rotate(self):
        logging.info("Rotating table")
        self.trigger("Rotate")

    # def Rotate_finished(self):
    #     logging.info("Rotating finished")
    #     self.trigger("Rotate_finished")

    def FillBottle_And_Tray_to_pump(self):
        logging.info("Filling bottle and moving tray to pump")
        self.trigger("FillBottle_And_Tray_to_pump")

    def Pump_to_measure_And_FillBottle(self):
        logging.info("Pumping to measure and filling bottle")
        self.trigger("Pump_to_measure_And_FillBottle")

    def stop(self):
        logging.info("Stopping the process")
        self.trigger("stop")


if __name__ == "__main__":
    # Create the table state machine
    table = TablePumpStateMachine()

    # Mapping user inputs to the respective state machine actions
    actions = {
        0: table.stop,
        1: table.Tray_to_pump,
        2: table.Rotate,
        3: table.FillBottle_And_Tray_to_pump,
        4: table.Pump_to_measure_And_FillBottle,
    }

    try:
        while True:
            # Display the options for user input
            next_action = int(
                input(
                    "Please select the next command: 0-stop; 1-tray_to_pump; 2-rotate; 3-fill_bottle_and_tray_to_pump; 4-pump_to_measure_and_fill_bottle: "
                )
            )

            # Trigger the corresponding action
            if next_action in actions:
                actions[next_action]()  # Call the appropriate method based on input
                logging.info(f"Table state: {table.state}")
            else:
                logging.error("Invalid input! Please select a valid command.")

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()
