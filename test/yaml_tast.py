import yaml


# Load YAML file and parse states
def parse_yaml(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    # Convert states into a dictionary for easy lookup
    return data


class Test:
    def initialize(self, x):
        print(f"i am initialize {x}")


if __name__ == "__main__":
    states_dict = parse_yaml("./test/test.yaml")
    # actions_list = states_dict["initialize"]["actions"]
    # trans_list = states_dict["initialize"]["transitions"]

    for state in states_dict["states"]:
        if "transitions" in state:
            print(state["transitions"])

    # T = Test()
    # trans_list["source"] = "initialize"
    # print(trans_list)
    # print(list(actions_list[0].keys())[0])
    # print(list(actions_list[0].values())[0])
    # method = getattr(T, list(actions_list[0].keys())[0])
    # print(method)
    # method("aaa")

    # dic = {"test": (1, 2, 3), "test2": ("ttt")}

    # print("test" in dic.keys())
