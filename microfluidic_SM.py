import logging
import time

from flask import Flask, render_template_string
from multiprocessing import Process, Manager
from multiprocessing.managers import SharedMemoryManager

from rotational_table_pump import TablePumpStateMachine
from rotational_table_measure import TableMeasureStateMachine
from gantry_SM import GantryStateMachine


# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Integrated Web Server</title>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
                background-color: #f0f0f0;
            }
            .window {
                position: absolute;
                border: 1px solid #ccc;
                overflow: hidden;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            iframe {
                border: 0;
            }
            #window1 {
                left: 20px;
                top: 20px;
                width: 45%;
                height: 80%;
            }
            #window2 {
                right: 20px;
                top: 20px;
                width: 45%;
                height: 80%;
            }
        </style>
    </head>
    <body>
        <div id="window1" class="window">
            <iframe src="http://localhost:8083" width="100%" height="100%"></iframe>
        </div>
        <div id="window2" class="window">
            <iframe src="http://localhost:8084" width="100%" height="100%"></iframe>
        </div>
    </body>
    </html>
    """
    )


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


if __name__ == "__main__":

    try:
        with Manager() as manager:
            # Define shared list sl = ["command", "feedback"]
            sl = manager.list(["waiting for command", "waiting for feedback"])

            # Start automatic state transitions
            p1 = Process(target=run_table_pump, args=(sl,))
            p2 = Process(target=run_gantry, args=(sl,))

            p1.start()
            p2.start()

            # Start the Flask server
            app.run(host="localhost", port=8085)

            # Wait for both processes to complete
            p1.join()
            p2.join()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
