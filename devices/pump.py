import os
import time

import unittest
from .pump_lib.qmixsdk import qmixbus
from .pump_lib.qmixsdk import qmixpump
from .pump_lib.qmixsdk import qmixanalogio


class SyringePump(unittest.TestCase):
    _bus_opened = False
    _bus_closed = False

    def __init__(self, pump_name):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.deviceconfig = os.path.join(script_dir, "PumpConfig")

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
        # print(self.pump_name)

    def initialize(self):
        # Empty the air ? Here or in the hardware.py
        # OOP problem: if for all the pump experiment in the future, "Empty the air" is always necessary, then put it here

        # Ramp up the flow ?
        pass

    def pump_enable(self):
        print(f"Enabling pump drive: {self.pump_name}")
        if self.pump.is_in_fault_state():
            self.pump.clear_fault()
        self.assertFalse(self.pump.is_in_fault_state())
        if not self.pump.is_enabled():
            self.pump.enable(True)
        self.assertTrue(self.pump.is_enabled())

    @staticmethod
    def wait_dosage_finished(pump, timeout_seconds):
        """
        The function waits until the last dosage command has finished
        until the timeout occurs.
        """

        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        message_timer = qmixbus.PollingTimer(500)
        result = True
        while (result == True) and not timer.is_expired():
            # Monitor the force if it is below the threshold
            # force_monitor(pump)

            time.sleep(0.1)
            if message_timer.is_expired():
                print(
                    f"Fill level: {pump.get_fill_level()}, \
                    Current force: {pump.read_force_sensor()}, \
                    {pump.is_force_safety_stop_active()}"
                )
                message_timer.restart()

            result = pump.is_pumping()
        return not result

    # def force_monitoring_config(self):
    #     self.assertTrue(self.pump.has_force_monitoring())
    #     self.pump.enable_force_monitoring(True)
    #     print("Force unit: ", self.pump.get_force_unit())
    #     print("Max device force: ", self.pump.get_max_device_force())

    #     # Setup the force limit
    #     self.pump.write_force_limit(0.11)
    def pressure_monitor(self):
        pressure_channel = qmixanalogio.AnalogInChannel()
        pressure_channel.lookup_channel_by_name(f"{self.pump_name}_AnIN1")
        print(f"Current status: {pressure_channel.read_status()}")
        print(f"Current pressure: {pressure_channel.read_input():.2f}")

    def si_units(self):
        """
        Setup the unit for volume and flow rate
        """
        print("Testing SI units...")
        self.pump.set_volume_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres)
        max_ml = self.pump.get_volume_max()
        print("Max. volume μl: ", max_ml, self.pump.get_volume_unit())

        self.pump.set_flow_unit(
            qmixpump.UnitPrefix.micro,
            qmixpump.VolumeUnit.litres,
            qmixpump.TimeUnit.per_second,
        )
        max_ml_s = self.pump.get_flow_rate_max()
        print("Max. flow μl/s: ", max_ml_s, self.pump.get_flow_unit())

    def aspirate(self):
        print("Testing aspiration...")
        max_volume = self.pump.get_volume_max() / 2
        max_flow = self.pump.get_flow_rate_max()
        self.pump.aspirate(max_volume, max_flow)

        finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, finished)

    def dispense(self):
        print("Testing dispensing...")
        max_volume = self.pump.get_volume_max() / 4
        max_flow = self.pump.get_flow_rate_max() / 2
        self.pump.dispense(max_volume, max_flow)
        finished = self.wait_dosage_finished(self.pump, 20)
        self.assertEqual(True, finished)

    def pump_volume(self):
        print("Testing pumping volume...")
        max_volume = self.pump.get_volume_max() / 10
        max_flow = self.pump.get_flow_rate_max() / 3

        self.pump.pump_volume(0 - max_volume, max_flow)  # aspirate
        finished = self.wait_dosage_finished(self.pump, 10)
        self.assertEqual(True, finished)

        self.pump.pump_volume(max_volume, max_flow)  # dispense
        finished = self.wait_dosage_finished(self.pump, 10)
        self.assertEqual(True, finished)

    def generate_flow(self):  # get deviation
        """
        Generate a continuous flow.

        A negative flow indicates aspiration and a positiove flow indicates
        dispension.
        """
        print("Testing generating flow...")
        max_flow = self.pump.get_flow_rate_max() / 3
        self.pump.generate_flow(max_flow)
        time.sleep(1)
        flow_is = self.pump.get_flow_is()
        self.assertAlmostEqual(max_flow, flow_is, places=4)
        finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, finished)

    def set_syringe_level(self):  # get deviation
        """
        Pumps fluid with the given flow rate until the requested fill level is reached.

        Depending on the requested fill level given in Level parameter this
        function may cause aspiration or dispension of fluid. This function only
        works properly for pump devices that support a fill level (eg. syringe
        pumps). Pumps like peristaltic pumps do not support a fill level and the
        function returns an error for unsupported pump types.
        """
        print("Testing set syringe fill level...")
        max_flow = self.pump.get_flow_rate_max() / 2
        max_volume = self.pump.get_volume_max() / 2
        self.pump.set_fill_level(max_volume, max_flow)
        finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, finished)

        fill_level_is = self.pump.get_fill_level()
        # self.assertAlmostEqual(max_volume, fill_level_is, places=1)
        print(fill_level_is)

        self.pump.set_fill_level(0, max_flow)
        finished = self.wait_dosage_finished(self.pump, 30)
        self.assertEqual(True, finished)

        fill_level_is = self.pump.get_fill_level()
        # self.assertAlmostEqual(0, fill_level_is, places=1)
        print(fill_level_is)

    def valve(self):
        print("Testing valve...")
        if not self.pump.has_valve():
            print("no valve installed")

        valve = self.pump.get_valve()
        valve_pos_count = valve.number_of_valve_positions()
        print("Valve positions: ", valve_pos_count)
        for i in range(valve_pos_count):
            valve.switch_valve_to_position(i)
            time.sleep(0.2)  # give valve some time to move to target
            valve_pos_is = valve.actual_valve_position()
            self.assertEqual(i, valve_pos_is)

    def switch_valve_to(self, position):
        """0: Close, 1: Refill, 2: Dispense, 3: Close"""
        if not self.pump.has_valve():
            print("no valve installed")
            return

        valve = self.pump.get_valve()
        valve.switch_valve_to_position(position)
        time.sleep(0.2)  # give valve some time to move to target

        # Ensure the valve is in the right position
        valve_pos_is = valve.actual_valve_position()
        print(f"Current valve position: {valve_pos_is}")
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
    pump.pump_enable()
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
    pump.pump_enable()
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

    pump1 = SyringePump("Nemesys_M_1_Pump")
    pump2 = SyringePump("Nemesys_M_2_Pump")
    pump3 = SyringePump("Nemesys_M_3_Pump")
    pump4 = SyringePump("Nemesys_M_4_Pump")
    pump5 = SyringePump("Nemesys_M_5_Pump")
    pump6 = SyringePump("Nemesys_M_6_Pump")
    pump7 = SyringePump("Nemesys_M_7_Pump")
    pump8 = SyringePump("Nemesys_M_8_Pump")

    # test(pump3)

    # multi_thread_test(pump3)
    # time.sleep(0.01)
    # # multi_thread_test(pump4)
    # # time.sleep(0.001)
    # multi_thread_test(pump7)
