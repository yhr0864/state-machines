import logging
import time
from multiprocessing import Process, Manager, Event
from flask import Flask, render_template, jsonify
from rotational_table_pump import TablePumpStateMachine
from gantry_SM import GantryStateMachine
from rotational_table_measure import TableMeasureStateMachine

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Global variables to hold our processes, shared list, and run flag
p1 = None
p2 = None
p3 = None
sl = None
run_flag = None


@app.route("/")
def index():
    return render_template("index_2.html")


@app.route("/start", methods=["POST"])
def start_processes():
    global p1, p2, p3, sl, run_flag
    if p1 is None and p2 is None and p3 is not None:
        sl = manager.list(["waiting for command", "waiting for feedback"])
        run_flag = manager.Event()
        p1 = Process(target=run_table_pump, args=(sl, run_flag))
        p2 = Process(target=run_gantry, args=(sl, run_flag))
        p3 = Process(target=run_table_measure, args=(sl, run_flag))
        p1.start()
        p2.start()
        p3.start()
        run_flag.set()  # Set the flag to start the processes
        return jsonify({"status": "started"})
    return jsonify({"status": "already running"})


@app.route("/stop", methods=["POST"])
def stop_processes():
    global p1, p2, p3, run_flag
    if p1 is not None and p2 is not None and p3 is not None:
        run_flag.clear()  # Clear the flag to stop the processes
        p1.join()
        p2.join()
        p3.join()
        p1 = None
        p2 = None
        p3 = None
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})


def run_gantry(shared_list, run_flag):
    gantry = GantryStateMachine(shared_list)
    # Mapping user inputs to the respective state machine actions
    actions = {
        "Stop": gantry.stop,
        "Tray_to_pump": gantry.getRequest_Tray_to_pump,
        "Measure_to_tray": gantry.getRequest_Measure_to_tray,
        "Pump_to_measure": gantry.getRequest_Pump_to_measure,
    }

    while True:
        if run_flag.is_set():
            # Display the options for user input
            next_action = gantry.shared_list[0]

            # Trigger the corresponding action
            if next_action in actions:
                actions[next_action]()  # Call the appropriate method based on input
                logging.info(f"Gantry state: {gantry.state}")
        else:
            gantry.machine.stop_server()
            break
        time.sleep(0.1)


def run_table_pump(shared_list, run_flag):
    table = TablePumpStateMachine(shared_list)
    while True:
        if run_flag.is_set():
            table.auto_run()
        else:
            table.machine.stop_server()
            break
        time.sleep(0.1)


def run_table_measure(shared_list, run_flag):
    table = TableMeasureStateMachine(shared_list)
    while True:
        if run_flag.is_set():
            table.auto_run()
        else:
            table.machine.stop_server()
            break
        time.sleep(0.1)


if __name__ == "__main__":
    with Manager() as manager:
        app.run(host="localhost", port=8086, debug=True)
