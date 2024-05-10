import os, sys, time
import csv


def open_csv_file(csv_file_path):
    edges_data = {}

    with open(csv_file_path, newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=";")
        next(csv_reader)  # Pomijamy nagłówek

        for row in csv_reader:
            edge = row[0]
            outcoming = row[1].split(",") if row[2] else []
            vehicles = {
                "moto": int(row[2]),
                "car": int(row[3]),
                "bus": int(row[4]),
                "truck": int(row[5]),
                "trailer": int(row[6]),
            }
            edges_data[edge] = {
                "outcoming": outcoming,
                "vehicles": vehicles,
            }

    # for edge, data in edges_data.items():
    #     print(f"Edge: {edge}")
    #
    #     print(f"Outcoming: {data['outcoming']}")
    #     print(f"Vehicles: {data['vehicles']}")
    #     print()
    return edges_data


def calculate_ratio(data_outcoming):
    pass


def allocate_traffic(edges_data):
    traffic_allocation = {}
    for edge, data in edges_data.items():
        outgoing_edges = data["outcoming"]
        total_outgoing_vehicles = 0
        traffic_allocation[edge] = {}
        traffic_allocation_scaler = 0

        for outgoing_edge in outgoing_edges:
            traffic_allocation_scaler += sum(
                edges_data[outgoing_edge]["vehicles"].values()
            )

        print(outgoing_edges, traffic_allocation_scaler)

        if outgoing_edges:
            total_outgoing_edges = len(outgoing_edges)

            for outgoing_edge in outgoing_edges:
                traffic_allocation[edge][outgoing_edge] = {}

                for vehicle, count in data["vehicles"].items():
                    if vehicle not in ["truck", "trailer"]:
                        traffic_allocation[edge][outgoing_edge][vehicle] = int(
                            count
                            * sum(edges_data[outgoing_edge]["vehicles"].values())
                            / traffic_allocation_scaler
                        )

    return traffic_allocation


def print_traffic_allocation(traffic_allocation):
    for edge, allocation in traffic_allocation.items():
        print(f"Edge: {edge}")
        for target_edge, vehicles in allocation.items():
            print(f"  To: {target_edge}")
            for vehicle, count in vehicles.items():
                print(f"    {vehicle}: {count}")
        print()


def main():
    csv_file_path = "data/daily_traffic_base.csv"
    edges_data = open_csv_file(csv_file_path)
    traffic_allocation = allocate_traffic(edges_data)
    print_traffic_allocation(traffic_allocation)


if __name__ == "__main__":
    main()
