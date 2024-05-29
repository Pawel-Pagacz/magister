import matplotlib.pyplot as plt
import csv

file_path = "output/logic_data.csv"

# Reading the CSV file
populations = []
sums = []

with open(file_path, newline="") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=";")
    header = next(csv_reader)
    for row in csv_reader:
        populations.append(int(row[0]))
        sums.append(float(row[3]))

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(populations, sums, color="b", s=20)
plt.xlabel("Population")
plt.ylabel("Sum")
plt.title("Population vs Sum")
plt.grid(True)
plt.show()
