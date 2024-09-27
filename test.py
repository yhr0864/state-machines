import logging
import time
from multiprocessing import Process, Manager
from flask import Flask, render_template_string, jsonify
from rotational_table_pump import TablePumpStateMachine
from gantry_SM import GantryStateMachine

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Shared state
shared_list = None
gantry = None
table = None


@app.route("/")
def index():
    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Integrated Control Panel</title>
        <style>
            .container { display: flex; height: 100vh; }
            .window { flex: 1; border: 1px solid #ccc; padding: 10px; }
            button { margin: 5px; }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        <script>
            function updateState(elementId, url) {
                $.get(url, function(data) {
                    $('#' + elementId).text(JSON.stringify(data, null, 2));
                });
            }
            function sendCommand(url) {
                $.post(url, function() {
                    updateState('gantryState', '/gantry_state');
                    updateState('tableState', '/table_state');
                });
            }
            $(document).ready(function() {
                setInterval(function() {
                    updateState('gantryState', '/gantry_state');
                    updateState('tableState', '/table_state');
                }, 1000);
            });
        </script>
    </head>
    <body>
        <div class="container">
            <div class="window">
                <h2>Gantry Control</h2>
                <button onclick="sendCommand('/gantry/stop')">Stop</button>
                <button onclick="sendCommand('/gantry/tray_to_pump')">Tray to Pump</button>
                <button onclick="sendCommand('/gantry/measure_to_tray')">Measure to Tray</button>
                <button onclick="sendCommand('/gantry/pump_to_measure')">Pump to Measure</button>
                <pre id="gantryState"></pre>
            </div>
            <div class="window">
                <h2>Table Pump Control</h2>
                <button onclick="sendCommand('/table/start')">Start</button>
                <button onclick="sendCommand('/table/stop')">Stop</button>
                <pre id="tableState"></pre>
            </div>
        </div>
    </body>
    </html>
    """
    )


@app.route("/gantry_state")
def gantry_state():
    return jsonify({"state": gantry.state, "shared_list": list(shared_list)})


@app.route("/table_state")
def table_state():
    return jsonify({"state": table.state, "shared_list": list(shared_list)})


@app.route("/gantry/<action>", methods=["POST"])
def gantry_action(action):
    actions = {
        "stop": gantry.stop,
        "tray_to_pump": gantry.getRequest_Tray_to_pump,
        "measure_to_tray": gantry.getRequest_Measure_to_tray,
        "pump_to_measure": gantry.getRequest_Pump_to_measure,
    }
    if action in actions:
        actions[action]()
    return "", 204


@app.route("/table/<action>", methods=["POST"])
def table_action(action):
    if action == "start":
        table.auto_run()
    elif action == "stop":
        table.stop()
    return "", 204


def run_gantry():
    global gantry
    while True:
        time.sleep(0.1)
        gantry.update()


def run_table_pump():
    global table
    while True:
        time.sleep(0.1)
        table.update()


if __name__ == "__main__":
    try:
        with Manager() as manager:
            shared_list = manager.list(["waiting for command", "waiting for feedback"])
            gantry = GantryStateMachine(shared_list)
            table = TablePumpStateMachine(shared_list)

            p1 = Process(target=run_table_pump)
            p2 = Process(target=run_gantry)
            p1.start()
            p2.start()

            # Start the Flask server
            app.run(host="localhost", port=8085, threaded=True)

            p1.join()
            p2.join()
    except KeyboardInterrupt:
        logging.info("Stopping the server...")
