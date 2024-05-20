import traci
import sumolib
import xml.etree.ElementTree as ET


class TrafficLightManager:
    def __init__(self, conn, steps, args, idx):
        self.steps = steps
        self.conn = conn
        self.args = args
        self.idx = idx
        self.average_waiting_time = 0
        self.controlled_lanes = [
            lane
            for tl in traci.trafficlight.getIDList()
            for lane in traci.trafficlight.getControlledLanes(tl)
        ]
        print(self.controlled_lanes)
        self.total_waiting_time = {}
        self.emissions_data = {}

    def get_traffic_light_logics(self):
        self.trafficlights = self.conn.trafficlight.getIDList()
        junctions = self.conn.junction.getIDList()
        self.traffic_light_logics = []
        for tl in self.trafficlights:
            logics = self.conn.trafficlight.getAllProgramLogics(tl)
            for logic in logics:
                self.traffic_light_logics.append((tl, logic))
        return self.traffic_light_logics

    def set_traffic_light_logics(self, new_logics):
        self.traffic_light_logics = new_logics
        for tl_id, logic in new_logics:
            traci.trafficlight.setProgram(tl_id, logic.programID)

            phases = []
            for phase in logic.phases:
                phases.append(
                    traci.trafficlight.Phase(
                        duration=phase.duration,
                        minDur=phase.minDur,
                        maxDur=phase.maxDur,
                        state=phase.state,
                    )
                )
            traci.trafficlight.setProgramLogic(
                tl_id,
                traci.trafficlight.Logic(
                    programID=logic.programID,
                    type=logic.type,
                    currentPhaseIndex=logic.currentPhaseIndex,
                    phases=phases,
                    subParameter=logic.subParameter,
                ),
            )

    def calculate_waiting_time(self):
        total_waiting_time = {}
        average_waiting_time = {}
        tree = ET.parse(f"output/queue_{self.args.simulation}{self.idx}.xml")
        root = tree.getroot()

        for timestep in root.findall("data"):
            lanes = timestep.find("lanes")
            if lanes is not None:
                for lane in lanes.findall("lane"):
                    lane_id = lane.get("id")
                    queueing_time = float(lane.get("queueing_time"))

                    for tl, _ in self.traffic_light_logics:
                        if lane_id in self.controlled_lanes:
                            if tl not in total_waiting_time:
                                total_waiting_time[tl] = 0.0
                            total_waiting_time[tl] += queueing_time
                            print(tl, total_waiting_time[tl])
                            average_waiting_time[tl] = (
                                total_waiting_time[tl] / self.steps
                            )
        self.average_waiting_time = average_waiting_time
        self.total_waiting_time = total_waiting_time

    def get_average_waiting_time(self):
        return self.average_waiting_time

    # def calculate_total_emission(self):
    #     for tl, logic in self.traffic_light_logics:
    #         for lane in self.conn.trafficlight.getControlledLanes(tl):
    #             CO2emission = self.conn.lane.getCO2Emission(lane)
    #             PMxemission = self.conn.lane.getPMxEmission(lane)
    #             HCemission = self.conn.lane.getHCEmission(lane)
    #             COemission = self.conn.lane.getCOEmission(lane)
    #             NOxemission = self.conn.lane.getNOxEmission(lane)
    #             CO2emission = self.conn.lane.getCO2Emission(lane)
    #             if tl in self.emissions_data:
    #                 self.emissions_data[tl]["PMx"] += PMxemission
    #                 self.emissions_data[tl]["HC"] += HCemission
    #                 self.emissions_data[tl]["CO"] += COemission
    #                 self.emissions_data[tl]["NOx"] += NOxemission
    #                 self.emissions_data[tl]["CO2"] += CO2emission
    #             else:
    #                 self.emissions_data[tl] = {
    #                     "PMx": PMxemission,
    #                     "HC": HCemission,
    #                     "CO": COemission,
    #                     "NOx": NOxemission,
    #                     "CO2": CO2emission,
    #                 }

    # def get_average_emission(self):
    #     self.average_emissions = {}
    #     for tl, average_emission in self.emissions_data.items():
    #         self.average_emissions[tl] = {}
    #         for emission_type, value in average_emission.items():
    #             self.average_emissions[tl][emission_type] = value / self.steps
    #     return self.average_emissions
