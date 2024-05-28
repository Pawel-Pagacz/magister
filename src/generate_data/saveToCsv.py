import csv
import os


def save_to_csv(logic_data, values_data, population, csv_file_path="logic_data.csv"):
    csv_data = []
    header = ["Population", "Logic", "Fitness", "Sum"]
    header.extend([f"{key}: {value}" for key, value in values_data.items()])
    values_data_str = ", ".join([f"'{k}': {v}" for k, v in values_data.items()])
    values_sum = sum(values_data.values())
    print(values_sum)
    row = [population, str(logic_data), values_data_str, values_sum]
    csv_data.append(row)

    file_exists = os.path.isfile(csv_file_path)
    file_has_data = os.path.getsize(csv_file_path) > 0 if file_exists else False

    with open(csv_file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists or not file_has_data:
            writer.writerow(["Population", "Logic", "Values", "Sum"])
        writer.writerows(csv_data)
