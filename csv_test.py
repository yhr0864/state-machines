import csv
import pandas as pd


# text = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]]

# with open("eggs.csv", mode="w", newline="") as file:
#     writer = csv.writer(file)

#     for row in text:
#         centered_row = [str(cell).center(2) for cell in row]
#         writer.writerow(centered_row)


headers = [
    "Time",
    "Run",
    "Mean volume diameter",
    "Mean area diameter",
    "Mean number diameter",
    "d(10%)",
    "d(20%)",
    "d(30%)",
    "d(40%)",
    "d(50%)",
    "d(60%)",
    "d(70%)",
    "d(80%)",
    "d(90%)",
    "d(95%)",
]

results_df = pd.DataFrame(columns=headers)
results_df.loc[len(results_df)] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
results_df.loc[len(results_df)] = [
    "avg",
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
]

print(results_df)
