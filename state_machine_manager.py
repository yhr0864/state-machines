import yaml
from typing import List, Dict, Tuple, Optional
from transitions_gui import WebMachine
import time

from hardware import Hardware


class StateMachineLoader:
    def __init__(self, config_path: str):
        """
        Initialize the loader with a path to the YAML configuration file.

        Args:
            config_path (str): Path to the YAML configuration file
        """
        self.config_path = config_path
        self.config = self._load_yaml()
        self.states, self.transitions = self._parse_config()

    def _load_yaml(self) -> dict:
        """Load and parse the YAML configuration file."""
        with open(self.config_path, "r") as file:
            return yaml.safe_load(file)

    def _parse_config(self) -> Tuple[List[str], List[Dict]]:
        """Parse the loaded configuration into states and transitions."""
        states = [state["name"] for state in self.config["states"]]
        transitions = []

        for state in self.config["states"]:
            if "transitions" in state:
                transition = state["transitions"]
                transition["source"] = state["name"]

                transitions.append(transition)

        return states, transitions

    def create_state_machine(self) -> type:
        """Create and return a configured StateMachine class."""
        states, transitions = self.states, self.transitions
        config = self.config

        states_dict = {state["name"]: state for state in self.config["states"]}

        class ConfiguredStateMachine:
            def __init__(self):
                # Explicitly define only the methods we want
                for state_name in states:
                    if state_name != "end":
                        setattr(self, state_name, self._create_state_method(state_name))
                    else:
                        setattr(self, state_name, self._end_state)

                self.machine = WebMachine(
                    model=self,
                    states=states,
                    transitions=transitions,
                    initial=config["initial_state"],
                    name=config["name"],
                    ignore_invalid_triggers=config["settings"][
                        "ignore_invalid_triggers"
                    ],
                    auto_transitions=False,
                    port=config["settings"]["port"],
                )
                self.hardware = Hardware()
                self.is_bottle_on_tray = True

            @staticmethod
            def _end_state() -> None:
                """Handle end state."""
                print("state machine is finished")

            def _create_state_method(self, state_name):
                """Create a method for a specific state."""

                actions_list = states_dict[state_name]["actions"]
                trans_info = states_dict[state_name]["transitions"]["trigger"]

                def state_method():
                    for action in actions_list:
                        # Check if the action needs arguments
                        if isinstance(action, dict):
                            action_name, args = next(iter(action.items()))
                        else:
                            # No arguments in action
                            action_name = action
                            args = None

                        # Check if the action corresponds to a method in hardware
                        if hasattr(self.hardware, action_name):
                            method = getattr(self.hardware, action_name)
                            # Call the method with or without arguments
                            if args is not None:
                                method(args)
                            else:
                                method()
                        else:
                            raise AttributeError(f"Action '{action_name}' not found.")

                    self.trigger(trans_info)

                return state_method

            def auto_run(self):
                """Run the state machine automatically."""
                while True:
                    if hasattr(self, self.state):
                        method = getattr(self, self.state)
                        method()
                    time.sleep(2)

        return ConfiguredStateMachine


# Example usage:
if __name__ == "__main__":
    import logging

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    loader = StateMachineLoader("state_machine_config.yaml")
    StateMachineClass = loader.create_state_machine()
    machine = StateMachineClass()

    # print(trans)

    try:
        # Start automatic state transitions
        machine.auto_run()

    except KeyboardInterrupt:
        # logging.info("Stopping the server...")
        machine.machine.stop_server()
