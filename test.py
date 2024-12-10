import time
import logging
import serial

from transitions_gui import WebMachine


class StateMachine:
    transitions = [
        {
            "trigger": "command_finished",
            "source": "A",
            "dest": "B",
        },
        {
            "trigger": "command_finished",
            "source": "B",
            "dest": "C",
        },
        {
            "trigger": "command_finished",
            "source": "C",
            "dest": "D",
        },
        {
            "trigger": "command_finished",
            "source": "D",
            "dest": "E",
        },
        {
            "trigger": "command_finished",
            "source": "E",
            "dest": "C",
            "conditions": "is_flag",
        },
        {
            "trigger": "command_finished",
            "source": "E",
            "dest": "F",
            "conditions": "is_flag",
        },
    ]

    def __init__(self):
        self.machine = WebMachine(
            model=self,
            states=["A", "B", "C", "D", "E", "F"],
            transitions=StateMachine.transitions,
            initial="A",
            name="Micro Fluidic System",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            # ordered_transitions=True,
            port=8083,
        )

        self.state_action_map = {
            "A": self.A,
            "B": self.B,
            "C": self.C,
            "D": self.D,
            "E": self.E,
            "F": self.F,
        }

        self.is_flag = True

    def A(self):
        self.trigger("command_finished")

    def B(self):
        self.trigger("command_finished")

    def C(self):
        self.trigger("command_finished")

    def D(self):
        self.trigger("command_finished")

    def E(self):
        self.trigger("command_finished")

    def F(self):
        logging.info("End")

    def auto_run(self):
        while True:
            action = getattr(self, self.state, lambda: "No action for this state")
            if action:
                action()
            time.sleep(1)


if __name__ == "__main__":
    import statistics

    # # Setup logging
    # logging.basicConfig(level=logging.INFO)

    # # Create the table state machine
    # table = StateMachine()

    # try:
    #     # Start automatic state transitions
    #     table.auto_run()

    # except KeyboardInterrupt:
    #     logging.info("Stopping the server...")
    #     table.machine.stop_server()
    # def measure_time():
    #     start_time = time.time()
    #     arduino = serial.Serial(port="COM8", baudrate=9600, timeout=0.1)
    #     arduino.write(bytes("command", "utf-8"))
    #     end_time = time.time()
    #     measured_time = end_time - start_time
    #     return measured_time

    # time_list = []
    # for i in range(100):
    #     t = measure_time()
    #     time_list.append(t)
    #     time.sleep(0.1)

    # print(statistics.mean(time_list))

    # class Base:
    #     def __init__(self, p):
    #         self.p = p

    #     def func(self):
    #         print(f"I am from Base {self.p}")

    # class Child(Base):
    #     def __init__(self, m):
    #         super().__init__(m)
    #         self.m = m

    #     def func(self):
    #         super().func()  # allow func overridden
    #         print(f"I am from Child {self.m}")

    # base = Base(10)
    # child = Child(20)

    # base.func()
    # child.func()
    # print(type(bytes([0x31])) == bytes)
    # print(bytes(bytes([0x31]), "utf-8"))

    import pyautogui

    pyautogui.click(2212, 105)
    time.sleep(25)
    pyautogui.click(x=2448, y=105)
