import functools
from concurrent.futures import ThreadPoolExecutor

from devices.arduino import ArduinoBoard
from devices.gantry import Gantry
from devices.pump import SyringePump

# Create a single global ThreadPoolExecutor
executor = ThreadPoolExecutor()


def decorator_parallel_executor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Submit the function to the shared executor
        future = executor.submit(func, *args, **kwargs)
        return future

    return wrapper


class Hardware:
    def __init__(self):
        self.gantry = Gantry()
        self.arduino = ArduinoBoard()
        self.pump1 = SyringePump("Nemesys_M_1_Pump")
        self.pump2 = SyringePump("Nemesys_M_2_Pump")
        self.pump3 = SyringePump("Nemesys_M_3_Pump")
        self.pump4 = SyringePump("Nemesys_M_4_Pump")
        self.pump5 = SyringePump("Nemesys_M_5_Pump")
        self.pump6 = SyringePump("Nemesys_M_6_Pump")
        self.pump7 = SyringePump("Nemesys_M_7_Pump")
        self.pump8 = SyringePump("Nemesys_M_8_Pump")

    def initialize(self):
        self.gantry.initialize()
        self.arduino.initialize()
        self.pump1.initialize()
        self.pump2.initialize()

    @decorator_parallel_executor
    def tray_to_pump(self, coord_on_tray, coord_on_table_p):
        self.gantry.move_from_to(coord_on_tray, coord_on_table_p)

    @decorator_parallel_executor
    def pump_to_measure(self, coord_on_table_p, coord_on_table_m):
        self.gantry.move_from_to(coord_on_table_p, coord_on_table_m)

    @decorator_parallel_executor
    def measure_to_tray(self, coord_on_table_m, coord_on_tray):
        self.gantry.move_from_to(coord_on_table_m, coord_on_tray)

    def rotate_table_p(self):
        self.arduino.send_command("motor1 rotate")

    def rotate_table_m(self):
        self.arduino.send_command("motor2 rotate")

    @decorator_parallel_executor
    def dose(self, pump: SyringePump):
        pump.pump_enable()
        pump.force_monitoring_config()
        pump.si_units()
        pump.dispense()

    def fill_bottle(self, target):
        # Parallelly dispensing
        match target:
            case "formula 1":
                self.dose(self.pump1)
                self.dose(self.pump2)
            case "formula 2":
                self.dose(self.pump2)
                self.dose(self.pump3)
            case _:
                print("Can not be formulated")

    @decorator_parallel_executor
    def measure_DLS(self):
        # Dip the measure rod in the sample
        self.arduino.send_command("rod_DLS extend")

        # Measuring

        # Measure finished
        self.arduino.send_command("rod_DLS retract")

    @decorator_parallel_executor
    def measure_UV(self):
        # Dip the measure rod in the sample
        self.arduino.send_command("rod_UV extend")

        # Measuring

        # Measure finished
        self.arduino.send_command("rod_UV retract")
