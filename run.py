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


def run_gantry(shared_list, queue, request_q):
    gantry = GantryStateMachine(shared_list)

    try:
        gantry.auto_run(queue, request_q)

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        gantry.machine.stop_server()


def run_table_pump(shared_list, queue, request_q):
    table = TablePumpStateMachine(shared_list, request_q)

    try:
        table.auto_run(queue)

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()


def run_table_measure(shared_list, queue, request_q):
    table = TableMeasureStateMachine(shared_list, request_q)

    try:
        table.auto_run(queue)

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()


if __name__ == "__main__":
    queue_pump = Queue()
    queue_gantry = Queue()
    queue_measure = Queue()

    request_queue = Queue()

    with Manager() as manager:
        # Define shared bool = False means not finished
        shared_list = manager.list([False, False, False])

        # Start automatic state transitions
        p1 = Process(
            target=run_table_pump,
            args=(shared_list, queue_pump, request_queue),
        )
        p2 = Process(
            target=run_gantry,
            args=(shared_list, queue_gantry, request_queue),
        )
        p3 = Process(
            target=run_table_measure,
            args=(shared_list, queue_measure, request_queue),
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
