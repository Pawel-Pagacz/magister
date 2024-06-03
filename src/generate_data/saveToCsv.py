import csv
import os
import traci
import sumolib


def save_to_csv(
    logic_data,
    values_mean,
    values_std,
    population,
    pop_size,
    csv_file_path="logic_data.csv",
):

    csv_data = []
    header = [f"Population {pop_size}", "Logic", "Travel Time Mean", "Travel Time Std"]
    row = [population, logic_data, values_mean, values_std]
    csv_data.append(row)

    file_exists = os.path.isfile(csv_file_path)
    file_has_data = os.path.getsize(csv_file_path) > 0 if file_exists else False

    with open(csv_file_path, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        if not file_exists or not file_has_data:
            writer.writerow(header)
        writer.writerows(csv_data)


def read_csv(file_path):
    with open(file_path, mode="r") as file:
        csv_reader = csv.reader(file, delimiter=";")
        header = next(csv_reader)
        data = [row for row in csv_reader]
    return header, data


def find_best_parent_and_worst_child(data):
    parent_rows = [row for row in data if row[0] == "0"]
    child_rows = [row for row in data if row[0] == "1"]

    parent_travel_times = [float(row[2]) for row in parent_rows]
    child_travel_times = [float(row[2]) for row in child_rows]

    best_parent_index = parent_travel_times.index(min(parent_travel_times))
    worst_child_index = child_travel_times.index(max(child_travel_times))

    return best_parent_index, worst_child_index, parent_rows, child_rows


def replace_best_parent_with_worst_child(
    data, best_parent_index, worst_child_index, parent_rows, child_rows
):
    best_parent = parent_rows[best_parent_index]
    worst_child = child_rows[worst_child_index]

    parent_row_index = data.index(best_parent)
    child_row_index = data.index(worst_child)

    data[child_row_index], data[parent_row_index] = (
        data[parent_row_index],
        data[child_row_index],
    )
    return data


def write_csv(file_path, header, data):
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(header)
        writer.writerows(data)


def write_line_to_file(fp, write_type, line):
    with open(fp, write_type) as f:
        f.write(line + "\n")
