import os, sys, subprocess
import traci
import numpy as np
import optparse
from src.trafficlightmanager import TrafficLightManager
from collections import namedtuple

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

Phase = namedtuple("Phase", ["duration", "state", "minDur", "maxDur"])
Logic = namedtuple(
    "Logic", ["programID", "type", "currentPhaseIndex", "phases", "subParameter"]
)


class SumoSim:
    def __init__(self, cfg_path, steps, algorithm, nogui, args, idx, logic=None):
        self.cfg_path = cfg_path
        self.steps = steps
        self.sumo_cmd = "sumo" if nogui else "sumo-gui"
        self.args = args
        self.idx = idx
        self.logic = logic

    def serverless_connect(self):

        sumoBinary = checkBinary(self.sumo_cmd)
        traci.start(
            [sumoBinary, "-c", self.cfg_path, "--no-step-log", "--no-warnings"],
            label="sim".format(self.idx),
        )

    def sim_step(self):
        self.conn.simulationStep()
        if self.steps % 100 == 0:
            print("Step: ", self.steps)
        self.steps += 1

    def gen_sim(self):
        self.serverless_connect()
        self.conn = traci.getConnection("sim".format(self.idx))
        self.tlm = TrafficLightManager(self.conn, self.steps)

        if self.logic == None:
            print("Connected to SUMO server")
            self.logic = self.tlm.get_traffic_light_logics()
            return self.close()
        else:
            print("Connected to SUMO server")
            print("Setting Traffic Light Logics")
            self.tlm.set_traffic_light_logics(self.logic)

        self.steps = 0

    def run(self):
        while (
            traci.simulation.getMinExpectedNumber() > 0 and self.steps < self.args.steps
        ):
            self.sim_step()
            self.tlm.calculate_total_waiting_time()
        return self.close()

    def close(self):
        self.steps = 0
        self.conn.close()
        return self.logic, self.tlm.get_average_waiting_time()


# -----------Try if serverless connect will not be working----------------
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
