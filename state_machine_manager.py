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
        """
        Parse the loaded configuration into states and transitions.

        Returns:
            Tuple[List[str], List[Dict]]: States and transitions lists
        """
        # Extract states
        states = [state["name"] for state in self.config["states"]]

        # Extract transitions
        transitions = []
        for state in self.config["states"]:
            if "transitions" in state:
                for trans in state["transitions"]:
                    transition = {
                        "trigger": trans["trigger"],
                        "source": state["name"],
                        "dest": trans["dest"],
                    }

                    # Handle special case for cycle_stage_4 transitions
                    if state["name"] == "cycle_stage_4":
                        if trans["dest"] == "cycle_stage_branch":
                            transition["conditions"] = "is_bottle_on_tray"
                        elif trans["dest"] == "after_cycle_stage":
                            transition["unless"] = "is_bottle_on_tray"

                    transitions.append(transition)

        return states, transitions

    def create_state_machine(self) -> type:
        """
        Create and return a configured StateMachine class.

        Returns:
            type: Configured StateMachine class
        """
        states, transitions = self.states, self.transitions

        class ConfiguredStateMachine:
            for state_name in states:
                setattr(self, state_name, self._create_state_method(state_name))

            def __init__(self):
                self.machine = WebMachine(
                    model=self,
                    states=states,
                    transitions=transitions,
                    initial=self.config["initial_state"],
                    name=self.config["name"],
                    ignore_invalid_triggers=self.config["settings"][
                        "ignore_invalid_triggers"
                    ],
                    auto_transitions=self.config["settings"]["auto_transitions"],
                    port=self.config["settings"]["port"],
                )

                self.is_bottle_on_tray = True

            def auto_run(self):
                """Run the state machine automatically."""
                while True:
                    if hasattr(self, self.state):
                        method = getattr(self, self.state)
                        method()
                    time.sleep(2)

            # Dynamically add state handler methods
            def _create_state_method(self, state_name):
                """Create a method for a specific state."""

                def state_method():
                    print(f"Executing state: {state_name}")
                    time.sleep(1)
                    self.trigger("command_finished")

                return state_method

        return ConfiguredStateMachine

    @property
    def machine_settings(self) -> dict:
        """Get the basic settings of the state machine."""
        return {
            "name": self.config["name"],
            "initial_state": self.config["initial_state"],
            "settings": self.config["settings"],
        }

    def get_states(self) -> List[str]:
        """Get the list of states."""
        return self.states

    def get_transitions(self) -> List[Dict]:
        """Get the list of transitions."""
        return self.transitions


# Example usage:
if __name__ == "__main__":
    import logging

    # Initialize the loader
    loader = StateMachineLoader("state-machine-config.yaml")

    # Print configuration information
    # print("Machine Settings:", loader.machine_settings)
    # print("States:", loader.get_states())
    # print("Transitions:", loader.get_transitions())

    # Create and run the state machine
    print("Create new state machine")
    StateMachineClass = loader.create_state_machine()
    machine = StateMachineClass()
    try:
        # Start automatic state transitions
        # machine.auto_run()
        methods = [
            method
            for method in dir(machine)
            if callable(getattr(machine, method)) and not method.startswith("__")
        ]

        print("Methods in MyClass instance:", methods)

    except KeyboardInterrupt:
        logging.info("Stopping the server...")
        machine.machine.stop_server()
