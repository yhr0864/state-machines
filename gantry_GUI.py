import time
import logging

from transitions_gui import WebMachine
from multiprocessing import shared_memory

# Setup logging
logging.basicConfig(level=logging.INFO)


class GantryStateMachine:
    states = ["idle", "tray_to_pump", "pump_to_measure", "measure_to_tray"]

    def __init__(self):
        # Initialize the state machine
        self.machine = WebMachine(
            model=self,
            states=GantryStateMachine.states,
            initial="idle",
            name="Gantry",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.machine.add_transition(trigger="timeup", source="green", dest="yellow")
        self.machine.add_transition(trigger="timeup", source="yellow", dest="red")
        self.machine.add_transition(trigger="timeup", source="red", dest="green")
