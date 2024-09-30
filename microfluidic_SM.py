import logging
import time

from flask import Flask, render_template
from multiprocessing import Process, Manager

# from multiprocessing.managers import SharedMemoryManager

from rotational_table_pump import TablePumpStateMachine
from rotational_table_measure import TableMeasureStateMachine
from gantry_SM import GantryStateMachine


# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def run_gantry(shared_list):
    gantry = GantryStateMachine(shared_list)
    # Mapping user inputs to the respective state machine actions
    actions = {
        "Stop": gantry.stop,
        "Tray_to_pump": gantry.getRequest_Tray_to_pump,
        "Measure_to_tray": gantry.getRequest_Measure_to_tray,
        "Pump_to_measure": gantry.getRequest_Pump_to_measure,
    }

    try:
        while True:
            # Display the options for user input
            next_action = gantry.shared_list[0]

            # Trigger the corresponding action
            if next_action in actions:
                actions[next_action]()  # Call the appropriate method based on input
                logging.info(f"Gantry state: {gantry.state}")

    except KeyboardInterrupt:  # Ctrl + C to stop the server
        logging.info("Stopping the server...")
        gantry.machine.stop_server()


def run_table_pump(shared_list):
    table = TablePumpStateMachine(shared_list)

    try:
        # Start automatic state transitions
        table.auto_run()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()


def run_table_measure(shared_list):
    table = TableMeasureStateMachine(shared_list)

    try:
        # Start automatic state transitions
        table.auto_run()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()


if __name__ == "__main__":
    with Manager() as manager:
        # Define shared list sl = ["command", "feedback"]
        sl = manager.list(["waiting for command", "waiting for feedback"])

        # Start automatic state transitions
        p1 = Process(target=run_table_pump, args=(sl,))
        p2 = Process(target=run_gantry, args=(sl,))
        p3 = Process(target=run_table_measure, args=(sl,))

        p1.start()
        p2.start()
        p3.start()

        # Start the Flask server
        app.run(host="localhost", port=8086)

        # Wait for both processes to complete
        p1.join()
        p2.join()
        p3.join()
