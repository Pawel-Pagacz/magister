import os, sys, subprocess
import traci
import numpy as np
import optparse
from src.trafficmetrics import *

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class SumoSim:
    def __init__(self, cfg_path, steps, algorithm, nogui, netdata, args, idx):
        self.cfg_path = cfg_path
        self.steps = steps
        self.sumo_cmd = "sumo" if nogui else "sumo-gui"
        self.netdata = netdata
        self.args = args
        self.idx = idx
        self.average_waiting_time = {}

    def serverless_connect(self):

        sumoBinary = checkBinary(self.sumo_cmd)
        traci.start(
            [sumoBinary, "-c", self.cfg_path, "--no-step-log", "--no-warnings"],
            label="sim".format(self.idx),
        )

    # def server_connect(self):
    #     sumoBinary = checkBinary(self.sumo_cmd)
    #     port = self.args.port + self.idx
    #     sumo_process = subprocess.Popen(
    #         [
    #             sumoBinary,
    #             "-c",
    #             self.cfg_fp,
    #             "--remote-port",
    #             str(port),
    #             "--no-warnings",
    #             "--no-step-log",
    #             "--random",
    #         ],
    #         stdout=None,
    #         stderr=None,
    #     )

    #     return traci.connect(port), sumo_process

    def sim_step(self):
        self.conn.simulationStep()
        if self.steps % 5000 == 0:
            print("Step: ", self.steps, self.average_waiting_time)
        self.steps += 1

    def gen_sim(self):
        self.serverless_connect()
        self.conn = traci.getConnection("sim".format(self.idx))
        print("Connected to SUMO server")
        traffic_schedule = self.get_traffic_lights()
        self.steps = 0

    def get_traffic_lights(self):
        trafficlights = self.conn.trafficlight.getIDList()
        junctions = self.conn.junction.getIDList()
        self.tl_juncs = set(trafficlights).intersection(set(junctions))
        green_phases_info = []

        for tl in self.tl_juncs:
            self.conn.trafficlight.subscribe(
                tl, [traci.constants.TL_COMPLETE_DEFINITION_RYG]
            )

            tldata = self.conn.trafficlight.getAllSubscriptionResults()
            logic = tldata[tl][traci.constants.TL_COMPLETE_DEFINITION_RYG][0]

            green_phases = [
                p
                for p in logic.getPhases()
                if "y" not in p.state and ("G" in p.state or "g" in p.state)
            ]
            for green_phase in green_phases:

                green_phases_info.append(
                    (
                        tl,
                        green_phase.state,
                        green_phase.duration,
                        green_phase.minDur,
                        green_phase.maxDur,
                    )
                )

        return green_phases_info

    def run(self):
        while (
            traci.simulation.getMinExpectedNumber() > 0 and self.steps < self.args.steps
        ):
            self.sim_step()
            self.calculate_average_waiting_time()
        print(self.get_average_waiting_time())
        self.close()

    def calculate_average_waiting_time(self):
        for tl in self.tl_juncs:
            total_waiting_time = 0
            for lane in self.conn.trafficlight.getControlledLanes(tl):
                waiting_time = traci.lane.getWaitingTime(lane)
                if waiting_time > 0:
                    total_waiting_time += waiting_time
                    self.average_waiting_time[tl] = total_waiting_time
                else:
                    pass

    def get_average_waiting_time(self):
        return self.average_waiting_time

    def close(self):
        self.conn.close()
