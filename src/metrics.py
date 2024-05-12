import os, sys
import traci

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class MetricsCalculator:
    def __init__(self, conn, tl_juncs):
        self.conn = conn
        self.tl_juncs = tl_juncs
        self.total_queue_length = {}
        self.emissions_data = {}

    def calculate_queue_metrics(self):
        for tl in self.tl_juncs:
            total_queue_length = 0
            for lane in self.conn.trafficlight.getControlledLanes(tl):
                queue_length = self.conn.lane.getLastStepHaltingNumber(lane)
                total_queue_length += queue_length
            self.total_queue_length[tl] = total_queue_length

    def calculate_emission_metrics(self):
        for tl in self.tl_juncs:
            if tl not in self.emissions_data:
                self.emissions_data[tl] = {
                    "PMx": 0,
                    "HC": 0,
                    "CO": 0,
                    "NOx": 0,
                    "CO2": 0,
                }

            for lane in self.conn.trafficlight.getControlledLanes(tl):
                CO2emission = self.conn.lane.getCO2Emission(lane)
                PMxemission = self.conn.lane.getPMxEmission(lane)
                HCemission = self.conn.lane.getHCEmission(lane)
                COemission = self.conn.lane.getCOEmission(lane)
                NOxemission = self.conn.lane.getNOxEmission(lane)

                self.emissions_data[tl]["PMx"] += PMxemission
                self.emissions_data[tl]["HC"] += HCemission
                self.emissions_data[tl]["CO"] += COemission
                self.emissions_data[tl]["NOx"] += NOxemission
                self.emissions_data[tl]["CO2"] += CO2emission

    def get_average_metrics(self, steps):
        average_queue_length = {}
        average_emissions = {}

        for tl in self.tl_juncs:
            average_queue_length[tl] = (
                self.total_queue_length[tl] / steps if steps > 0 else 0
            )
            average_emissions[tl] = {}

            for emission_type, value in self.emissions_data[tl].items():
                average_emissions[tl][emission_type] = value / steps if steps > 0 else 0

        return average_queue_length, average_emissions
