from hardware import Hardware


class StateMachine:
    def __init__(self) -> None:
        pass

    def before_cycle_stage_1(self):
        # Send command
        Hardware.tray_to_pump()
        time.sleep(0.1)
        Hardware.rotate_table_p()
        time.sleep(0.1)
        Hardware.fill_bottle()

        # transition
        self.trigger("Finished")

    def before_cycle_stage_1(self):
        # Send command
        Hardware.tray_to_pump()
        time.sleep(0.1)
        Hardware.rotate_table_p()
        time.sleep(0.1)
        Hardware.fill_bottle()

        # transition
        self.trigger("Finished")

    ############################

    def before_cycle_stage_9(self):
        # Send command
        Hardware.tray_to_pump()
        time.sleep(0.1)
        Hardware.rotate_table_p()
        time.sleep(0.1)
        Hardware.fill_bottle()

        # transition
        self.trigger("Finished")
