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
                "moto": int(row[2]) / 2,
                "car": int(row[3]) / 2,
                "bus": int(row[4]) / 2,
                "truck": int(row[5]) / 2,
                "trailer": int(row[6]) / 2,
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


# def merge_edges(traffic_allocation):
#     merged_traffic_allocation = traffic_allocation.copy()
#     start_edges = ["G", "E", "H", "C", "B", "F"]

#     for start_edge in start_edges:
#         visited_edges = set()

#         def merge(start_edge, current_edge):
#             visited_edges.add(current_edge)

#             if current_edge in traffic_allocation:
#                 for end_edge, vehicles in traffic_allocation[current_edge].items():
#                     # print(current_edge, end_edge)
#                     for end_edge in traffic_allocation[current_edge]:
#                         visited_edges.add(end_edge)
#                         print(visited_edges)
#                     if end_edge in start_edges and end_edge != start_edge:
#                         print(start_edge, end_edge, current_edge)
#                         if end_edge in merged_traffic_allocation[start_edge]:
#                             for vehicle_type, count in vehicles.items():
#                                 if (
#                                     end_edge
#                                     not in merged_traffic_allocation[start_edge]
#                                 ):
#                                     merged_traffic_allocation[start_edge][end_edge] = {}
#                                 merged_traffic_allocation[start_edge][end_edge][
#                                     vehicle_type
#                                 ] = (
#                                     merged_traffic_allocation[start_edge][end_edge].get(
#                                         vehicle_type, 0
#                                     )
#                                     + count
#                                 )
#                         else:
#                             merged_traffic_allocation[start_edge][
#                                 end_edge
#                             ] = vehicles.copy()
#                             for vehicle_type, count in vehicles.items():
#                                 merged_traffic_allocation[current_edge][end_edge][
#                                     vehicle_type
#                                 ] = 0
#                                 merged_traffic_allocation[start_edge][current_edge][
#                                     vehicle_type
#                                 ] -= count

#                     elif end_edge not in visited_edges:
#                         # If not a start edge and not visited yet, consider it as an intermediate edge
#                         merge(start_edge, end_edge)

#         merge(start_edge, start_edge)

#     return merged_traffic_allocation


def print_traffic_allocation(traffic_allocation):
    for edge, allocation in traffic_allocation.items():
        print(f"Edge: {edge}")
        for target_edge, vehicles in allocation.items():
            print(f"  To: {target_edge}")
            for vehicle, count in vehicles.items():
                print(f"    {vehicle}: {count}")
        print()


def generate_od_files(traffic_allocation):
    moto_data = {}
    car_data = {}
    bus_data = {}
    for from_taz, to_taz_data in traffic_allocation.items():
        for to_taz, vehicle_data in to_taz_data.items():
            for vehicle_type, count in vehicle_data.items():
                if vehicle_type == "moto":
                    if (from_taz, to_taz) not in moto_data:
                        moto_data[(from_taz, to_taz)] = count
                    else:
                        moto_data[(from_taz, to_taz)] += count
                elif vehicle_type == "car":
                    if (from_taz, to_taz) not in car_data:
                        car_data[(from_taz, to_taz)] = count
                    else:
                        car_data[(from_taz, to_taz)] += count
                elif vehicle_type == "bus":
                    if (from_taz, to_taz) not in bus_data:
                        bus_data[(from_taz, to_taz)] = count
                    else:
                        bus_data[(from_taz, to_taz)] += count
    return moto_data, car_data, bus_data


def write_data_to_file(data, vehicle_type, city):
    filename = f"networks/{city}/{city}_{vehicle_type}.od"
    with open(filename, "w") as f:
        f.write("$O;D2\n* From-Time To-Time\n0.00 24000.00\n* Factor\n1.00\n")
        for (from_taz, to_taz), count in data.items():
            f.write(f"{from_taz} {to_taz} {count}\n")


def main():
    city = "wielun"
    csv_file_path = "data/daily_traffic_base.csv"
    edges_data = open_csv_file(csv_file_path)
    traffic_allocation = allocate_traffic(edges_data)
    print(traffic_allocation)
    moto_data, car_data, bus_data = generate_od_files(traffic_allocation)
    write_data_to_file(moto_data, "moto", city)
    write_data_to_file(car_data, "car", city)
    write_data_to_file(bus_data, "bus", city)


if __name__ == "__main__":
    main()
