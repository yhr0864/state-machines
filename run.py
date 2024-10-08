import logging
import time
import atexit

from flask import Flask, render_template, request
from multiprocessing import Process, Manager, Queue

# from multiprocessing.managers import SharedMemoryManager

from rotational_table_pump import TablePumpStateMachine
from rotational_table_measure import TableMeasureStateMachine
from gantry_SM import GantryStateMachine


# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


def cleanup_processes(processes):
    for process in processes:
        if process.is_alive():
            process.terminate()
            process.join()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/control", methods=["POST"])
def control():
    command = request.form.get("command")
    if command:
        queue_pump.put(command)
        queue_gantry.put(command)
        queue_measure.put(command)
        logging.info(f"Received command from web interface: {command}")
    return ("", 204)


def run_gantry(shared_list, queue):
    gantry = GantryStateMachine(shared_list)
    # Mapping user inputs to the respective state machine actions
    actions = {
        "Tray_to_pump": gantry.getRequest_Tray_to_pump,
        "Measure_to_tray": gantry.getRequest_Measure_to_tray,
        "Pump_to_measure": gantry.getRequest_Pump_to_measure,
    }
    commands = {
        "0": gantry.start,
        "1": gantry.stop,
    }

    try:
        while True:
            if not queue.empty():  # Check if there's any input in the queue
                user_input = queue.get()  # Get the input from the queue
                if user_input in commands:
                    commands[user_input]()
                    logging.info(
                        f"Received command {user_input}. Gantry state: {gantry.state}"
                    )
                else:
                    logging.warning(f"Invalid command: {user_input}")
            else:
                if gantry.running:
                    # Display the options for user input
                    # next_actions = gantry.shared_list
                    next_action = gantry.shared_list[0]

                    # print(next_actions)
                    # Trigger the corresponding action
                    if next_action in actions:
                        actions[next_action]()
                        logging.info(f"Gantry state: {gantry.state}")

    except KeyboardInterrupt:  # Ctrl + C to stop the server
        logging.info("Stopping the server...")
        gantry.machine.stop_server()


def run_table_pump(shared_list, queue):
    table = TablePumpStateMachine(shared_list)

    try:
        # Start automatic state transitions
        table.auto_run(queue)

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()


def run_table_measure(shared_list, queue):
    table = TableMeasureStateMachine(shared_list)

    try:
        # Start automatic state transitions
        table.auto_run(queue)

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()


if __name__ == "__main__":
    queue_pump = Queue()
    queue_gantry = Queue()
    queue_measure = Queue()

    with Manager() as manager:
        # Define shared list sl = ["command", "feedback"]
        sl = manager.list(["waiting for command", "waiting for feedback"])

        # Start automatic state transitions
        p1 = Process(
            target=run_table_pump,
            args=(
                sl,
                queue_pump,
            ),
        )
        p2 = Process(
            target=run_gantry,
            args=(
                sl,
                queue_gantry,
            ),
        )
        p3 = Process(
            target=run_table_measure,
            args=(
                sl,
                queue_measure,
            ),
        )

        p1.start()
        p2.start()
        p3.start()

        atexit.register(cleanup_processes, [p1, p2, p3])

        # Start the Flask server
        app.run(host="localhost", port=8086)

        # Wait for both processes to complete
        # p1.join()
        # p2.join()
        # p3.join()
