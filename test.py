from transitions_gui import WebMachine


class MatterStateMachine(object):

    states = ["solid", "liquid", "gas", "plasma"]
    transitions = [
        {
            "trigger": "melt",
            "source": "solid",
            "dest": "liquid",
            "before": "make_hissing_noises",
            "after": "disappear",
        },
        {
            "trigger": "evaporate",
            "source": "liquid",
            "dest": "gas",
            "after": "disappear",
        },
    ]

    def __init__(self):
        self.machine = WebMachine(
            model=self,
            states=MatterStateMachine.states,
            transitions=MatterStateMachine.transitions,
            initial="solid",
            name="Matter",
            ignore_invalid_triggers=True,
            auto_transitions=False,
            port=8083,
        )

    def make_hissing_noises(self):
        print("HISSSSSSSSSSSSSSSS")

    def disappear(self):
        print("where'd all the liquid go?")


lump = MatterStateMachine()

lump.melt()
