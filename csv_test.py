import csv

text = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]]

with open("eggs.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(text)
