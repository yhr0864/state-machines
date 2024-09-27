import logging

from multiprocessing import Process
from multiprocessing.managers import SharedMemoryManager

from rotational_table_pump import TablePumpStateMachine
from rotational_table_measure import TableMeasureStateMachine
from gantry_SM import GantryStateMachine


# Setup logging
logging.basicConfig(level=logging.INFO)


def run_gantry(sl, gantry):
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
            next_action = sl[0]

            # Trigger the corresponding action
            if next_action in actions:
                actions[next_action]()  # Call the appropriate method based on input
                logging.info(f"Gantry state: {gantry.state}")
            else:
                logging.error("Invalid input! Please select a valid command.")

    except KeyboardInterrupt:  # Ctrl + C to stop the server
        logging.info("Stopping the server...")
        gantry.machine.stop_server()


if __name__ == "__main__":
    # Create the table state machine
    table = TablePumpStateMachine()
    gantry = GantryStateMachine()

    try:
        with SharedMemoryManager() as smm:
            sl = smm.ShareableList(range(2000))
            # Start automatic state transitions
            p1 = Process(table.auto_run, args=(sl,))
            p2 = Process(
                run_gantry,
                args=(
                    sl,
                    gantry,
                ),
            )

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()
