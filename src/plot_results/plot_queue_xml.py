import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from collections import defaultdict


# Funkcja do parsowania XML i wyciągania danych dla podanych LaneIDs
def parse_xml(file_path, lane_ids):
    tree = ET.parse(file_path)
    root = tree.getroot()

    timesteps = []
    queueing_times = defaultdict(float)
    queueing_lengths = defaultdict(float)
    queueing_lengths_experimental = defaultdict(float)

    for data in root.findall("data"):
        timestep = float(data.get("timestep")) / 3600
        timesteps.append(timestep)
        lanes = data.find("lanes")
        if lanes is not None:
            for lane_id in lane_ids:
                lane = lanes.find(f'./lane[@id="{lane_id}"]')
                if lane is not None:
                    queueing_times[timestep] += float(lane.get("queueing_time", 0))
                    queueing_lengths[timestep] += float(lane.get("queueing_length", 0))
                    queueing_lengths_experimental[timestep] += float(
                        lane.get("queueing_length_experimental", 0)
                    )

    # Convert defaultdict to list of values sorted by timesteps
    timesteps = sorted(timesteps)
    queueing_times = [queueing_times[t] for t in timesteps]
    queueing_lengths = [queueing_lengths[t] for t in timesteps]
    queueing_lengths_experimental = [
        queueing_lengths_experimental[t] for t in timesteps
    ]

    return timesteps, queueing_times, queueing_lengths, queueing_lengths_experimental


# Funkcja do rysowania wykresów
def plot_data(
    timesteps, queueing_times, queueing_lengths, queueing_lengths_experimental, lane_ids
):
    plt.figure(figsize=(12, 6))

    plt.plot(timesteps, queueing_times, label="Queueing Time")
    # plt.plot(timesteps, queueing_lengths, label="Queueing Length")
    # plt.plot(
    #     timesteps, queueing_lengths_experimental, label="Queueing Length Experimental"
    # )

    plt.xlabel("Timestep")
    plt.ylabel("Values")
    plt.title(f"Queueing Data for TL No. 429723386")
    plt.legend()
    plt.grid(True)
    plt.show()


# Ścieżka do pliku XML
file_path = "output/queue_wielun0.xml"
lane_ids = [
    "438404111_0",
    "438404111_1",
    "-549008043#2_0",
    "-549008043#2_1",
    "549008046#0_1",
]  # Lista LaneID

# Parsowanie danych
timesteps, queueing_times, queueing_lengths, queueing_lengths_experimental = parse_xml(
    file_path, lane_ids
)

# Rysowanie wykresów
plot_data(
    timesteps, queueing_times, queueing_lengths, queueing_lengths_experimental, lane_ids
)
