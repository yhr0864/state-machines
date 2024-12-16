import time
import logging

from transitions_gui import WebMachine

from hardware import Hardware
from utils import states, transitions


class StateMachine:
    def __init__(self) -> None:
        self.machine = WebMachine(
            model=self,
            states=states,
            transitions=transitions,
            initial="initialize",
            name="Micro Fluidic System",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.hardware = Hardware()
        self.is_bottle_on_tray = True

    def initialize(self):
        # Initialize all the hardwares
        # Hardware.initialize()

        # transition
        self.trigger("initialize_finished")

    def before_cycle_stage_1(self):
        # Send command
        # Hardware.tray_to_pump()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_2(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_3(self):
        # Send command
        # Hardware.fill_bottle()
        # Hardware.tray_to_pump()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_4(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_5(self):
        # Send command
        # Hardware.fill_bottle()
        # Hardware.pump_to_measure()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_6(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_7(self):
        # Send command
        # Hardware.tray_to_pump()
        # Hardware.measure_UV()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_8(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_9(self):
        # Send command
        # Hardware.fill_bottle()
        # Hardware.pump_to_measure()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_10(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_11(self):
        # Send command
        # Hardware.tray_to_pump()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_12(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_13(self):
        # Send command
        # Hardware.fill_bottle()
        # Hardware.pump_to_measure()
        # Hardware.measure_DLS
        # Hardware.measure_UV()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_14(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_15(self):
        # Send command
        # Hardware.tray_to_pump()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_16(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_17(self):
        # Send command
        # Hardware.fill_bottle()
        # Hardware.measure_DLS()
        # Hardware.measure_UV()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    ############################

    def cycle_stage_1(self):
        # Send command
        # Hardware.measure_to_tray()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        # Hardware.pump_to_measure()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_4(self):
        # Send command
        # Hardware.measure_DLS()
        # Hardware.measure_UV()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_branch(self):
        # Send command
        # Hardware.tray_to_pump()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_6(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_7(self):
        # Send command
        # Hardware.fill_bottle()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    ########################################

    def after_cycle_stage(self):
        # Send command
        # Hardware.rotate_table_p()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_2(self):
        # Send command
        # Hardware.measure_to_tray()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_3(self):
        # Send command
        # Hardware.pump_to_measure()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_4(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_5(self):
        # Send command
        # Hardware.measure_DLS()
        # Hardware.measure_UV()
        # Hardware.measure_to_tray()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_6(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_7(self):
        # Send command
        # Hardware.measure_DLS()
        # Hardware.measure_to_tray()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_8(self):
        # Send command
        # Hardware.rotate_table_m()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_9(self):
        # Send command
        # Hardware.measure_to_tray()
        # time.sleep(1)

        # transition
        self.trigger("command_finished")

    def auto_run(self):
        while True:
            action = getattr(self, self.state, lambda: "No action for this state")
            if action:
                action()
            time.sleep(2)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create the table state machine
    table = StateMachine()

    try:
        # Start automatic state transitions
        table.auto_run()

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        table.machine.stop_server()
