import time
from transitions_gui import WebMachine  # noqa
from multiprocessing import Process, Manager


class TrafficLightStateMachine(object):
    states = ["green", "yellow", "red"]
    transitions = [
        ["timeup", "Green", "Red"],
        ["timeup", "Red", "Yellow"],
        ["timeup", "Yellow", "Green"],
    ]

    def __init__(self, shared_state):
        # Initialize the state machine with shared state
        self.shared_state = shared_state
        self.machine = WebMachine(
            model=self,
            states=TrafficLightStateMachine.states,
            transitions=TrafficLightStateMachine.transitions,
            initial="green",
            name="Traffic Light",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

        self.machine.add_transition(trigger="timeup", source="green", dest="red")
        self.machine.add_transition("timeup", "red", "yellow")
        self.machine.add_transition("timeup", "yellow", "green")

    @property
    def state(self):
        # Return the state from the shared memory
        return self.shared_state.value

    @state.setter
    def state(self, value):
        # Update the state in the shared memory
        self.shared_state.value = value

    def timeup(self):
        # Transition to the next state and update the shared memory
        self.trigger("timeup")
        self.shared_state.value = self.state


class Vehicle:
    states = ["stop", "moving"]
    transitions = [
        ["start_engine", "stop", "moving"],
        ["brake", "moving", "stop"],
    ]

    def __init__(self):
        # Initialize the state machine for the vehicle
        self.machine = WebMachine(
            model=self,
            states=Vehicle.states,
            transitions=Vehicle.transitions,
            initial="stop",
            name="Car",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8084,
        )

        self.machine.add_transition("start_engine", "stop", "moving")
        self.machine.add_transition("brake", "moving", "stop")

    def handle_traffic_light(self, traffic_light_state):
        # This is the switcher pattern integrated into the vehicle class
        method_name = "handle_" + str(traffic_light_state)
        method = getattr(self, method_name, lambda: "No action for this state")
        return method()

    def handle_red(self):
        if self.state == "moving":
            self.brake()
            return "Car stops"
        else:
            return "Car is already stopped"

    def handle_green(self):
        if self.state == "stop":
            self.start_engine()
            return "Car moves"
        else:
            return "Car is already moving"

    def handle_yellow(self):
        # Yellow could be handled with a default message or another action
        return "Car is waiting..."


def run_light(traffic_light):
    while True:
        time.sleep(2)
        traffic_light.timeup()
        print(f"Traffic light is now: {traffic_light.state}")


def run_car(traffic_light):
    car = Vehicle()
    while True:
        time.sleep(1)
        action_result = car.handle_traffic_light(traffic_light.state)

        if action_result:
            print(action_result)


if __name__ == "__main__":
    with Manager() as manager:
        shared_state = manager.Value("s", "green")
        traffic_light = TrafficLightStateMachine(shared_state)

        # Start processes for traffic light and vehicle logic
        p1 = Process(target=run_light, args=(traffic_light,))
        p2 = Process(target=run_car, args=(traffic_light,))

        p1.start()
        p2.start()

        # Wait for processes to complete
        p1.join()
        p2.join()
