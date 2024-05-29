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
        self.total_waiting_time = {}
        self.emissions_data = {}
        self.controlled_lanes = {}
        for tl in self.conn.trafficlight.getIDList():
            self.controlled_lanes[tl] = self.conn.trafficlight.getControlledLanes(tl)

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
                        if lane_id in self.controlled_lanes.get(tl, []):
                            if tl not in total_waiting_time:
                                total_waiting_time[tl] = 0.0
                            total_waiting_time[tl] += queueing_time
                            average_waiting_time[tl] = round(
                                total_waiting_time[tl] / self.steps, 2
                            )
        self.average_waiting_time = average_waiting_time
        self.total_waiting_time = total_waiting_time

    def get_average_waiting_time(self):
        return self.average_waiting_time
