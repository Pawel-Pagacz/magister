import csv
import os
import traci
import sumolib


def save_to_csv(
    logic_data, values_data, population, pop_size, csv_file_path="logic_data.csv"
):
    csv_data = []
    header = [f"Population {pop_size}", "Logic", "Fitness", "Sum"]
    values_sum = sum(values_data.values())
    row = [population, logic_data, values_data, values_sum]
    csv_data.append(row)

    file_exists = os.path.isfile(csv_file_path)
    file_has_data = os.path.getsize(csv_file_path) > 0 if file_exists else False

    with open(csv_file_path, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        if not file_exists or not file_has_data:
            writer.writerow(header)
        writer.writerows(csv_data)
