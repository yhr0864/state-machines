from devices.arduino import ArduinoBoard
from devices.gantry import Gantry
from devices.pump import SyringePump


class Hardware:
    def __init__(self) -> None:
        self.gantry = Gantry()
        self.arduino = ArduinoBoard()
        self.pump1 = SyringePump(1)
        self.pump2 = SyringePump(2)

    def tray_to_pump(self):
        self.gantry.move_from_to(coord_on_tray, coord_on_table_p)

    def pump_to_measure(self):
        self.gantry.move_from_to(coord_on_table_p, coord_on_table_m)

    def measure_to_tray(self):
        self.gantry.move_from_to(coord_on_table_m, coord_on_tray)

    def rotate_table_p(self):
        self.arduino.send_command("rotate motor1")

    def rotate_table_m(self):
        self.arduino.send_command("rotate motor2")

    def fill_bottle(self):
        # parallelly dispensing
        self.pump1.dispense()
        self.pump2.dispense()

    def measure(self):
        pass
