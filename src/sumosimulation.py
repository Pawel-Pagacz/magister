import os, sys, subprocess
import traci
import numpy as np
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
    def __init__(self, cfg_path, steps, nogui, args, idx, population_idx, logic=None):
        self.cfg_path = cfg_path
        self.steps = steps
        self.sumo_cmd = "sumo" if nogui else "sumo-gui"
        self.args = args
        self.idx = idx
        self.logic = logic
        self.population_idx = population_idx

    def serverless_connect(self):
        sumoBinary = checkBinary(self.sumo_cmd)
        traci.start(
            [
                sumoBinary,
                "-c",
                self.cfg_path,
                "--no-step-log",
                "--no-warnings",
                "--queue-output",
                f"output/queue_{self.args.simulation}{self.idx}.xml",
            ],
            label="sim".format(self.idx),
        )

    def sim_step(self):
        self.conn.simulationStep()
        if self.steps % 40000 == 0:
            print(
                "Pop: ",
                self.population_idx,
                "Procs Idx: ",
                self.idx,
                "Step: ",
                self.steps,
            )
        self.steps += 1

    def gen_sim(self):
        self.serverless_connect()
        self.conn = traci.getConnection("sim".format(self.idx))
        self.tlm = TrafficLightManager(self.conn, self.steps, self.args, self.idx)
        self.steps = 0
        if self.logic == None:
            self.logic = self.tlm.get_traffic_light_logics()
            return self.close()
        else:
            self.tlm.set_traffic_light_logics(self.logic)

    def run(self):
        while (
            traci.simulation.getMinExpectedNumber() > 0 and self.steps < self.args.steps
        ):
            self.sim_step()
        return self.close()

    def close(self):
        self.conn.close()
        self.steps = 0
        if self.idx > -1:
            self.tlm.calculate_waiting_time()
        return self.logic, self.tlm.get_average_waiting_time()
