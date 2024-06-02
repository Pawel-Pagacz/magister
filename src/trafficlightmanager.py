import traci
import sumolib
import time


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
        self.departure_times = {}
        self.travel_times = {}

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

            phases = [
                traci.trafficlight.Phase(
                    duration=phase.duration,
                    minDur=phase.minDur,
                    maxDur=phase.maxDur,
                    state=phase.state,
                )
                for phase in logic.phases
            ]
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
        for v in self.conn.vehicle.getArrivedIDList():
            route = self.conn.vehicle.getRoute(v)
            for edge in route:
                if edge not in self.total_waiting_time:
                    self.total_waiting_time[edge] = 0
                self.total_waiting_time[
                    edge
                ] += self.conn.vehicle.getAccumulatedWaitingTime(v)
        return self.total_waiting_time

    def calculate_travel_time(self):
        for v in self.conn.simulation.getDepartedIDList():
            self.departure_times[v] = self.conn.simulation.getTime()

        for v in self.conn.simulation.getArrivedIDList():
            arrival_time = self.conn.simulation.getTime()
            travel_time = arrival_time - self.departure_times[v]
            self.travel_times[v] = travel_time
            del self.departure_times[v]
        return self.travel_times

    def get_average_waiting_time(self):
        if len(self.total_waiting_time) == 0:
            return 0
        self.average_waiting_time = sum(self.total_waiting_time.values()) / len(
            self.total_waiting_time
        )
        print(self.average_waiting_time)
        return self.average_waiting_time

    def get_average_travel_time(self):
        if len(self.travel_times) == 0:
            return 0
        print(sum(self.travel_times.values()) / len(self.travel_times))
        return sum(self.travel_times.values()) / len(self.travel_times)
