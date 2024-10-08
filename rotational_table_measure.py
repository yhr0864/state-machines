import time
import logging
from transitions_gui import WebMachine

# Setup logging
logging.basicConfig(level=logging.INFO)


class TableMeasureStateMachine:
    states = [
        "Empty_Empty_Empty",
        "Empty_Empty_Bottle",
        "Bottle_Empty_Empty",
        "BottleM1_Empty_Bottle",
        "Bottle_BottleM1_Empty",
        "BottleM1_BottleM2_Bottle",
        "Bottle_BottleM1_BottleM2",
        "BottleM1_BottleM2_Empty",
    ]

    transitions = [
        {
            "trigger": "Pump_to_measure",
            "source": "Empty_Empty_Empty",
            "dest": "Empty_Empty_Bottle",
        },
        {
            "trigger": "Rotate",
            "source": "Empty_Empty_Bottle",
            "dest": "Bottle_Empty_Empty",
        },
        {
            "trigger": "UV_Measure_And_Pump_to_measure",
            "source": "Bottle_Empty_Empty",
            "dest": "BottleM1_Empty_Bottle",
        },
        {
            "trigger": "Rotate",
            "source": "BottleM1_Empty_Bottle",
            "dest": "Bottle_BottleM1_Empty",
        },
        {
            "trigger": "Pump_to_measure_And_UV_Measure_And_DLS_Measure",
            "source": "Bottle_BottleM1_Empty",
            "dest": "BottleM1_BottleM2_Bottle",
        },
        {
            "trigger": "Rotate",
            "source": "BottleM1_BottleM2_Bottle",
            "dest": "Bottle_BottleM1_BottleM2",
        },
        {
            "trigger": "Measure_to_tray_And_UV_Measure_And_DLS_Measure",
            "source": "Bottle_BottleM1_BottleM2",
            "dest": "BottleM1_BottleM2_Empty",
        },
        {
            "trigger": "Pump_to_measure",
            "source": "BottleM1_BottleM2_Empty",
            "dest": "BottleM1_BottleM2_Bottle",
        },
    ]

    def __init__(self):
        # Initialize the state machine with shared state
        self.machine = WebMachine(
            model=self,
            states=TableMeasureStateMachine.states,
            transitions=TableMeasureStateMachine.transitions,
            initial="Empty_Empty_Empty",
            name="Rotational Table Pump",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

    def Rotate(self):
        logging.info("Rotating table")
        self.trigger("Rotate")

    def Pump_to_measure(self):
        logging.info("Transitioning from pump to measure")
        self.trigger("Pump_to_measure")

    def UV_Measure_And_Pump_to_measure(self):
        logging.info("Measuring with UV and moving from pump to measure")
        self.trigger("UV_Measure_And_Pump_to_measure")

    def Pump_to_measure_And_UV_measure_And_DLS_measure(self):
        logging.info("Measuring with UV and DLS and moving from pump to measure")
        self.trigger("Pump_to_measure_And_UV_Measure_And_DLS_Measure")

    def Measure_to_tray_And_UV_measure_And_DLS_measure(self):
        logging.info("Measuring with UV and DLS and moving from measure to tray")
        self.trigger("Measure_to_tray_And_UV_Measure_And_DLS_Measure")

    def stop(self):
        logging.info("Stopping the process")
        self.trigger("stop")


if __name__ == "__main__":
    # Create the table state machine
    table = TableMeasureStateMachine()

    # Mapping user inputs to the respective state machine actions
    actions = {
        0: table.stop,
        1: table.Pump_to_measure,
        2: table.Rotate,
        3: table.UV_Measure_And_Pump_to_measure,
        4: table.Pump_to_measure_And_UV_measure_And_DLS_measure,
        5: table.Measure_to_tray_And_UV_measure_And_DLS_measure,
    }

    try:
        while True:
            # Display the options for user input
            next_action = int(
                input(
                    "Please select the next command:\n"
                    "0-stop; 1-pump_to_measure; 2-rotate; "
                    "3-UV_Measure_And_Pump_to_measure; "
                    "4-Pump_to_measure_And_UV_measure_And_DLS_measure; "
                    "5-Measure_to_tray_And_UV_measure_And_DLS_measure; "
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
