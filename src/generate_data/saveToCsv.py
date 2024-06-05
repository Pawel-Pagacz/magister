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
    header = [f"Population {pop_size}", "Logic", "Travel Time Mean", "Travel Time; Std"]
    row = [population, logic_data, values_mean, values_std]
    csv_data.append(row)

    file_exists = os.path.isfile(csv_file_path)
    file_has_data = os.path.getsize(csv_file_path) > 0 if file_exists else False

    with open(csv_file_path, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        if not file_exists or not file_has_data:
            writer.writerow(header)
        writer.writerows(csv_data)


def save_scores_to_csv(scores):
    header = [
        "Population",
        "Individual",
        "Logic",
        "Travel Time Mean",
        "Travel Time Std",
    ]
    with open("output/scores.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for population_idx, individuals in scores.items():
            for individual_idx, entry in individuals.items():
                writer.writerow(
                    [
                        population_idx,
                        individual_idx,
                        entry["logic"],
                        entry["mean"],
                        entry["std"],
                    ]
                )


def write_line_to_file(fp, write_type, line):
    with open(fp, write_type) as f:
        f.write(line + "\n")
