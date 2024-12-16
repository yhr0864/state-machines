import functools
from concurrent.futures import ThreadPoolExecutor

from devices.arduino import ArduinoBoard
from devices.gantry import Gantry
from devices.pump import SyringePump
from devices.dls import DLS_Analyzer

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
        # self.gantry = Gantry()
        # self.arduino = ArduinoBoard()
        # self.pump1 = SyringePump("Nemesys_M_1_Pump")
        # self.pump2 = SyringePump("Nemesys_M_2_Pump")
        # self.pump3 = SyringePump("Nemesys_M_3_Pump")
        # self.pump4 = SyringePump("Nemesys_M_4_Pump")
        # self.pump5 = SyringePump("Nemesys_M_5_Pump")
        # self.pump6 = SyringePump("Nemesys_M_6_Pump")
        # self.pump7 = SyringePump("Nemesys_M_7_Pump")
        # self.pump8 = SyringePump("Nemesys_M_8_Pump")

        # self.dls = DLS_Analyzer()
        pass

    def initialize(self):
        # self.gantry.initialize()
        # self.arduino.initialize()
        # self.dls.initialize()
        # self.pump1.initialize()
        # self.pump2.initialize()
        print("hardwares are initializing")

    @decorator_parallel_executor
    def tray_to_pump(self, coord: tuple):
        coord_on_tray = coord[0]
        coord_on_table_p = coord[1]
        # self.gantry.move_from_to(coord_on_tray, coord_on_table_p)
        print("tray to pump")

    @decorator_parallel_executor
    def pump_to_measure(self, coord: tuple):
        coord_on_table_p = coord[0]
        coord_on_table_m = coord[1]
        # self.gantry.move_from_to(coord_on_table_p, coord_on_table_m)
        print("pump to measure")

    @decorator_parallel_executor
    def measure_to_tray(self, coord: tuple):
        coord_on_table_m = coord[0]
        coord_on_tray = coord[1]
        # self.gantry.move_from_to(coord_on_table_m, coord_on_tray)
        print("measure to tray")

    def rotate_table_p(self):
        # return self.arduino.send_command("motor1 rotate")
        print("rotate p")

    def rotate_table_m(self):
        # return self.arduino.send_command("motor2 rotate")
        print("rotate m")

    @decorator_parallel_executor
    def dose(self, pump: SyringePump):
        # pump.pump_enable()
        # pump.force_monitoring_config()
        # pump.si_units()
        # pump.dispense()
        print("dose")

    def fill_bottle(self, target: tuple):
        target = target[0]
        # Parallelly dispensing
        # match target:
        #     case "formula 1":
        #         self.dose(self.pump1)
        #         self.dose(self.pump2)
        #     case "formula 2":
        #         self.dose(self.pump2)
        #         self.dose(self.pump3)
        #     case _:
        #         print("Can not be formulated")
        print("fill bottle")

    @decorator_parallel_executor
    def measure_DLS(self):
        # # Dip the measure rod in the sample
        # self.arduino.send_command("rod_DLS extend")

        # # Measuring

        # # Measure finished
        # self.arduino.send_command("rod_DLS retract")
        print("measure dls")

    @decorator_parallel_executor
    def measure_UV(self):
        # # Dip the measure rod in the sample
        # self.arduino.send_command("rod_UV extend")

        # # Measuring

        # # Measure finished
        # self.arduino.send_command("rod_UV retract")
        print("measure uv")
