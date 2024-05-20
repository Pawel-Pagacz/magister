import traci
import sumolib


class TrafficLightManager:
    def __init__(self, conn, steps):
        self.steps = steps
        self.conn = conn
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

    def calculate_total_waiting_time(self):
        total_waiting_time = 0
        for tl, logic in self.traffic_light_logics:
            for lane in self.conn.trafficlight.getControlledLanes(tl):
                waiting_time = self.conn.lane.getWaitingTime(lane)
                if waiting_time > 0:
                    total_waiting_time += waiting_time
                    # print(total_waiting_time)
                    if tl in self.total_waiting_time:
                        self.total_waiting_time[tl] += total_waiting_time
                        # print("HERE", self.total_waiting_time)
                    else:
                        self.total_waiting_time[tl] = total_waiting_time
                        # print("OUPS", self.total_waiting_time)
                else:
                    pass

    def get_average_waiting_time(self):
        self.average_waiting_time = {}
        # print(self.total_waiting_time)
        for tl, waiting_time in self.total_waiting_time.items():
            self.average_waiting_time[tl] = waiting_time / self.steps
        return self.average_waiting_time

    def calculate_total_emission(self):
        for tl, logic in self.traffic_light_logics:
            for lane in self.conn.trafficlight.getControlledLanes(tl):
                CO2emission = self.conn.lane.getCO2Emission(lane)
                PMxemission = self.conn.lane.getPMxEmission(lane)
                HCemission = self.conn.lane.getHCEmission(lane)
                COemission = self.conn.lane.getCOEmission(lane)
                NOxemission = self.conn.lane.getNOxEmission(lane)
                CO2emission = self.conn.lane.getCO2Emission(lane)
                if tl in self.emissions_data:
                    self.emissions_data[tl]["PMx"] += PMxemission
                    self.emissions_data[tl]["HC"] += HCemission
                    self.emissions_data[tl]["CO"] += COemission
                    self.emissions_data[tl]["NOx"] += NOxemission
                    self.emissions_data[tl]["CO2"] += CO2emission
                else:
                    self.emissions_data[tl] = {
                        "PMx": PMxemission,
                        "HC": HCemission,
                        "CO": COemission,
                        "NOx": NOxemission,
                        "CO2": CO2emission,
                    }

    def get_average_emission(self):
        self.average_emissions = {}
        for tl, average_emission in self.emissions_data.items():
            self.average_emissions[tl] = {}
            for emission_type, value in average_emission.items():
                self.average_emissions[tl][emission_type] = value / self.steps
        return self.average_emissions
