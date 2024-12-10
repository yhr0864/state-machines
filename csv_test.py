import csv


# text = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]]

# with open("eggs.csv", mode="w", newline="") as file:
#     writer = csv.writer(file)

#     for row in text:
#         centered_row = [str(cell).center(2) for cell in row]
#         writer.writerow(centered_row)


import pandas as pd

# Example DataFrame
mean_values = pd.DataFrame([1.12345, 2.56789, 3.98765, 4.54321])

# Round and convert the first row
row_list = mean_values.round(2).iloc[0].tolist()
print(type(row_list), row_list)  # Output: [1.12, 3.99]
