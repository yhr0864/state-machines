import json


def generate_bottle_data(rows, cols):
    """
    BottleID: (e.g. 10x10)
        1 2 3 ... 10
        11
        ...
        91 ...    100
    """
    data = {}
    for row in range(rows):
        for col in range(cols):
            bottle_id = row * cols + col + 1
            position = {"row": row + 1, "col": col + 1}

            # Only for example
            property_type = "empty" if (row + col) % 2 == 0 else "apple juice"
            bottle_info = {
                "position": position,
                "proportion": [50, 50],
                "solution": ["apple juice", "orange juice"],
                "property": "empty",
            }
            data[bottle_id] = bottle_info
    return data


def read_bottle_data(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data


if __name__ == "__main__":
    # Generate data for 10x10 grid
    bottle_data = generate_bottle_data(10, 10)

    # Save to a JSON file
    file_path = "./bottle_data.json"
    with open(file_path, "w") as json_file:
        json.dump(bottle_data, json_file, indent=4)

    # Read the bottle data from the previously created JSON file
    bottle_data_read = read_bottle_data("./bottle_data.json")
    print(bottle_data_read)  # Display the first 5 entries to verify the content
