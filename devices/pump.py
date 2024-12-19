import os
import time

import unittest
from pump_lib.qmixsdk import qmixbus
from pump_lib.qmixsdk import qmixpump
from pump_lib.qmixsdk import qmixanalogio


class SyringePump(unittest.TestCase):
    _bus_opened = False
    _bus_closed = False

    def __init__(self, pump_name, pressure_limit):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.deviceconfig = os.path.join(script_dir, "pump_lib/PumpConfig")
        self.pressure_limit = pressure_limit

        # Make sure bus only opened once
        if not self._bus_opened:
            print("Opening bus with deviceconfig ", self.deviceconfig)
            self.bus = qmixbus.Bus()
            self.bus.open(self.deviceconfig, "")
            self.__class__._bus_opened = True
            print("Starting bus communication...")
            self.bus.start()

        self.pump = qmixpump.Pump()
        self.pump.lookup_by_name(pump_name)
        self.pump_name = self.pump.get_device_name()

        self.pressure_channel = qmixanalogio.AnalogInChannel()
        self.pressure_channel.lookup_channel_by_name(f"{self.pump_name}_AnIN1")

        self.finished = None
        # print(self.pump_name)

    def initialize(self):
        # Empty the air ? Here or in the hardware.py
        # OOP problem: if for all the pump experiment in the future, "Empty the air" is always necessary, then put it here

        # Ramp up the flow ?

        # Enable the pump
        print(f"Enabling pump drive: {self.pump_name}")
        if self.pump.is_in_fault_state():
            self.pump.clear_fault()
        self.assertFalse(self.pump.is_in_fault_state())
        if not self.pump.is_enabled():
            self.pump.enable(True)
        self.assertTrue(self.pump.is_enabled())

        # Check Valves
        if not self.pump.has_valve():
            raise ModuleNotFoundError("no valve installed")
        self.valve = self.pump.get_valve()

        # Ckeck if pressuren sensor works
        self.current_pressure_sensor_status = self.pressure_channel.read_status()
        print(f"Current sensor status: {self.current_pressure_sensor_status}")

    def wait_dosage_finished(self, timeout_seconds):
        """
        The function waits until the last dosage command has finished
        until the timeout occurs.
        """

        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        message_timer = qmixbus.PollingTimer(500)
        result = True
        while (result == True) and not timer.is_expired():
            # Monitor the force if it is below the threshold
            current_pressure = self.pressure_channel.read_input()
            if current_pressure >= self.pressure_limit:
                print(
                    f"Warning: Current pressure {current_pressure} is over the limit. Pump stops!"
                )
                self.pump.stop_pumping()
                break

            time.sleep(0.1)
            if message_timer.is_expired():
                print(
                    f" Dosed volume: {self.pump.get_dosed_volume()}, Flow rate: {self.pump.get_flow_is()}, \
                    Fill level: {self.pump.get_fill_level()}, Current pressure: {current_pressure:.2f}"
                )
                message_timer.restart()

            result = self.pump.is_pumping()
        return not result

    def pressure_monitor(self):
        # Test this to ensure the unit of pressure: bar?
        pressure_channel = qmixanalogio.AnalogInChannel()
        pressure_channel.lookup_channel_by_name(f"{self.pump_name}_AnIN1")
        current_pressure = pressure_channel.read_status()
        print(f"Current status: {current_pressure}")
        print(f"Current pressure: {current_pressure:.2f}")
        return current_pressure

    def si_units(self):
        """
        Setup the unit for volume and flow rate
        """

        print("Testing SI units...")
        self.pump.set_volume_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres)
        max_ml = self.pump.get_volume_max()
        print("Max. volume ml: ", max_ml, self.pump.get_volume_unit())

        self.pump.set_flow_unit(
            qmixpump.UnitPrefix.milli,
            qmixpump.VolumeUnit.litres,
            qmixpump.TimeUnit.per_second,
        )
        max_ml_s = self.pump.get_flow_rate_max()
        print("Max. flow ml/s: ", max_ml_s, self.pump.get_flow_unit())

    def aspirate(self, volume, flow):
        """
        Aspirate a certain volume with a certain flow rate.
        """

        self.switch_valve_to(1)
        self.pump.aspirate(volume, flow)

        self.finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, self.finished)
        return self.finished

    def dispense(self, volume, flow):
        """
        Dispense a certain volume with a certain flow rate.
        """

        self.switch_valve_to(2)
        self.pump.dispense(volume, flow)
        self.finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, self.finished)
        return self.finished

    def refill(self):
        self.switch_valve_to(1)
        flow = 0 - self.pump.get_flow_rate_max() / 10
        self.finished = self.generate_flow(flow)
        return self.finished

    def empty(self):
        self.switch_valve_to(2)
        flow = self.pump.get_flow_rate_max() / 10
        self.finished = self.generate_flow(flow)
        return self.finished

    def generate_flow(self, flow):  # get deviation
        """
        Generate a continuous flow.

        A negative flow indicates aspiration and a positiove flow indicates
        dispension.
        """

        self.pump.generate_flow(flow)
        self.finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, self.finished)
        return self.finished

    def switch_valve_to(self, position: int):
        """0: Close, 1: Aspirate, 2: Dispense"""

        self.valve.switch_valve_to_position(position)
        time.sleep(0.2)  # give valve some time to move to target

        # Ensure the valve is in the right position
        valve_pos_is = self.valve.actual_valve_position()
        self.assertEqual(position, valve_pos_is)

    def stop_pump(self):
        """
        Immediately stop pumping.
        """

        self.pump.stop_pumping()

    @staticmethod
    def stop_all_pumps():
        """
        Immediately stop pumping off all pumps.
        """
        qmixpump.Pump.stop_all_pumps()

    def capi_close(self):
        # Make sure bus only closed once
        if not self._bus_closed:
            print("Closing bus...")
            self.bus.stop()
            self.bus.close()
            self.__class__._bus_closed = True
            print("Bus closed")
        else:
            print("Bus closed")


def test(pump: SyringePump):
    pump.initialize()
    pump.pressure_monitor()
    pump.si_units()

    # pump.aspirate()
    # pump.dispense()
    # pump.pump_volume()
    # pump.generate_flow()
    # pump.set_syringe_level()  # Test with this one first
    # pump.valve()
    pump.switch_valve_to(1)
    time.sleep(3)
    pump.switch_valve_to(0)
    time.sleep(1)
    # pump.capi_close()


from concurrent.futures import ThreadPoolExecutor
import functools
import time

# Create a single global ThreadPoolExecutor
executor = ThreadPoolExecutor()


def decorator_parallel_executor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Submit the function to the shared executor
        future = executor.submit(func, *args, **kwargs)
        return future

    return wrapper


@decorator_parallel_executor
def multi_thread_test(pump: SyringePump):
    pump.initialize()
    pump.pressure_monitor()
    pump.si_units()

    # pump.aspirate()
    # pump.dispense()
    # pump.pump_volume()
    # pump.generate_flow()
    # pump.set_syringe_level()  # Test with this one first
    # pump.valve()

    # valve switch test
    # pump.switch_valve_to(0)
    # time.sleep(2)
    # pump.switch_valve_to(1)
    # time.sleep(3)
    # pump.switch_valve_to(2)
    # time.sleep(2)
    # pump.switch_valve_to(3)
    # time.sleep(2)
    pump.capi_close()


if __name__ == "__main__":

    pump1 = SyringePump("Nemesys_M_1_Pump", 30)
    pump2 = SyringePump("Nemesys_M_2_Pump", 30)
    pump3 = SyringePump("Nemesys_M_3_Pump", 12)
    pump4 = SyringePump("Nemesys_M_4_Pump", 12)
    pump5 = SyringePump("Nemesys_M_5_Pump", 12)
    pump6 = SyringePump("Nemesys_M_6_Pump", 24)
    pump7 = SyringePump("Nemesys_M_7_Pump", 24)
    pump8 = SyringePump("Nemesys_M_8_Pump", 30)

    # test(pump3)

    # multi_thread_test(pump3)
    # time.sleep(0.01)
    # # multi_thread_test(pump4)
    # # time.sleep(0.001)
    # multi_thread_test(pump7)
