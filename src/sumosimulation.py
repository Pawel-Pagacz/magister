import os, sys, subprocess
import traci
import numpy as np
from src.trafficlightmanager import TrafficLightManager
import time

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class SumoSim:
    def __init__(self, nogui, args, idx, population_idx, logic=None):
        self.cfg_path = args.cfg_path
        self.steps = args.steps
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
            ],
            label="sim".format(self.idx),
        )

    def sim_step(self):
        self.conn.simulationStep()
        self.tlm.calculate_travel_time()
        if self.steps % 10000 == 0:
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
            self.close()
            return self.logic, self.tlm.get_average_travel_time()
        else:
            self.tlm.set_traffic_light_logics(self.logic)

    def run(self):
        start_time = time.time()
        simulation_time = 0
        while (
            traci.simulation.getMinExpectedNumber() > 0 and self.steps < self.args.steps
        ):
            if self.steps % 10000 == 0:
                end_time = time.time()
                simulation_time = end_time - start_time
                print("Time taken for 10000 steps: ", simulation_time, " seconds")
                start_time = time.time()
            if self.args.simulation == "wielun" and simulation_time > 120:
                print(
                    self.steps,
                    "steps took more than 120 seconds, exiting with fitness 999999",
                )
                self.sim_step()
                return self.logic, 9999

            self.sim_step()
        self.close()
        if self.idx > -1:
            return self.logic, self.tlm.get_average_travel_time()

    def sim_stats(self):
        return self.tlm.get_average_travel_time(), self.tlm.get_std_travel_time()

    def close(self):
        self.conn.close()
        self.steps = 0
