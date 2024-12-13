import yaml
from typing import List, Dict, Tuple, Optional
from transitions_gui import WebMachine
import time


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
                for trans in state["transitions"]:
                    transition = {
                        "trigger": trans["trigger"],
                        "source": state["name"],
                        "dest": trans["dest"],
                    }

                    if state["name"] == "cycle_stage_4":
                        if trans["dest"] == "cycle_stage_branch":
                            transition["conditions"] = "is_bottle_on_tray"
                        elif trans["dest"] == "after_cycle_stage":
                            transition["unless"] = "is_bottle_on_tray"

                    transitions.append(transition)

        return states, transitions

    def create_state_machine(self) -> type:
        """Create and return a configured StateMachine class."""
        states, transitions = self.states, self.transitions
        config = self.config

        class ConfiguredStateMachine:
            def __init__(self):
                # Explicitly define only the methods we want
                for state_name in states:
                    setattr(self, state_name, self._create_state_method(state_name))

                self.machine = WebMachine(
                    model=self,
                    states=states,
                    transitions=transitions,
                    initial=config["initial_state"],
                    name=config["name"],
                    ignore_invalid_triggers=config["settings"][
                        "ignore_invalid_triggers"
                    ],
                    auto_transitions=False,  # Prevent auto-transition method creation
                    port=config["settings"]["port"],
                )

                self.is_bottle_on_tray = True

            def _create_state_method(self, state_name):
                """Create a method for a specific state."""

                def state_method():
                    print(f"Executing state: {state_name}")
                    time.sleep(1)
                    self.trigger("command_finished")

                return state_method

            def auto_run(self):
                """Run the state machine automatically."""
                while True:
                    if hasattr(self, self.state):
                        method = getattr(self, self.state)
                        method()
                    time.sleep(2)

        return ConfiguredStateMachine, transitions


# Example usage:
if __name__ == "__main__":
    import logging

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    loader = StateMachineLoader("state_machine_config.yaml")
    StateMachineClass, trans = loader.create_state_machine()
    machine = StateMachineClass()

    print(trans)
    # # Verify available methods
    # print(
    #     "Available methods:",
    #     [
    #         method
    #         for method in dir(machine)
    #         # if not method.startswith("_")
    #         # and not method.startswith("is_")
    #         # and not method.startswith("may_")
    #     ],
    # )

    try:
        # Start automatic state transitions
        machine.auto_run()

    except KeyboardInterrupt:
        # logging.info("Stopping the server...")
        machine.machine.stop_server()
