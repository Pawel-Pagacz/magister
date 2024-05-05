import os, sys, subprocess
import traci
import numpy as np

from src.trafficsignalcontroller import TrafficSignalController
from src.tsc_factory import tsc_factory
from src.helper_funcs import write_to_log

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    from sumolib import checkBinary
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class SumoSim:
    def __init__(self, cfg_path, sim_len, algorithm, nogui, netdata, args, idx):
        self.cfg_path = cfg_path
        self.sim_len = sim_len
        self.tsc = tsc
        self.sumo_cmd = "sumo" if nogui else "sumo-gui"
        self.netdata = netdata
        self.args = args
        self.idx = idx

    def serverless_connect(self):
        traci.start(
            [
                self.sumo_cmd,
                "-c",
                self.cfg_path,
                "--no-step-log",
                "--no-warnings",
                "--random",
            ]
        )

    def server_connect(self):
        sumoBinary = checkBinary(self.sumo_cmd)
        port = self.args.port + self.idx
        sumo_process = subprocess.Popen(
            [
                sumoBinary,
                "-c",
                self.cfg_path,
                "--remote-port",
                str(port),
                "--no-warnings",
                "--no-step-log",
                "--random",
            ],
            stdout=None,
            stderr=None,
        )

        return traci.connect(port), sumo_process

    def get_traffic_lights(self):
        trafficlights = self.conn.trafficlight.getIDList()
        junctions = self.conn.junction.getIDList()
        tl_juncs = set(trafficlights).intersection(set(junctions))
        tls = []

        for tl in tl_juncs:
            self.conn.trafficlight.subscribe(
                tl, [traci.constants.TL_COMPLETE_DEFINITION_RYG]
            )

            tldata = self.conn.trafficlight.getAllSubscriptionResults()
            logic = tldata[tl][traci.constants.TL_COMPLETE_DEFINITION_RYG][0]
            # logic = self.conn.trafficlight.getCompleteRedYellowGreenDefinition(tl)[0]
            green_phases = [
                p.state
                for p in logic.getPhases()
                if "y" not in p.state and ("G" in p.state or "g" in p.state)
            ]
            if len(green_phases) > 1:
                tls.append(tl)

    def create_tsc(self, rl_stats, exp_replays, eps, neural_networks=None):
        self.tl_junc = self.get_traffic_lights()
        if not neural_networks:
            neural_networks = {tl: None for tl in self.tl_junc}
        # create traffic signal controllers for the junctions with lights
        self.tsc = {
            tl: tsc_factory(
                self.args.tsc,
                tl,
                self.args,
                self.netdata,
                rl_stats[tl],
                exp_replays[tl],
                neural_networks[tl],
                eps,
                self.conn,
            )
            for tl in self.tl_junc
        }

    def update_netdata(self):
        tl_junc = self.get_traffic_lights()
        tsc = {
            tl: TrafficSignalController(
                self.conn, tl, self.args.mode, self.netdata, 2, 3
            )
            for tl in tl_junc
        }

        for t in tsc:
            self.netdata["inter"][t]["incoming_lanes"] = tsc[t].incoming_lanes
            self.netdata["inter"][t]["green_phases"] = tsc[t].green_phases

        all_intersections = set(self.netdata["inter"].keys())
        # only keep intersections that we want to control
        for i in all_intersections - tl_junc:
            del self.netdata["inter"][i]

        return self.netdata

    def sim_step(self):
        self.conn.simulationStep()
        self.t += 1

    def run(self):
        # execute simulation for desired length
        while self.t < self.sim_len:
            # run all traffic signal controllers in network
            for t in self.tsc:
                self.tsc[t].run()
            self.sim_step()

    def get_intersection_subscription(self):
        tl_data = {}
        lane_vehicles = {l: {} for l in self.lanes}
        for tl in self.tl_junc:
            tl_data[tl] = self.conn.junction.getContextSubscriptionResults(tl)
            if tl_data[tl] is not None:
                for v in tl_data[tl]:
                    lane_vehicles[tl_data[tl][v][traci.constants.VAR_LANE_ID]][v] = (
                        tl_data[tl][v]
                    )
        return lane_vehicles

    def sim_stats(self):
        tt = self.get_travel_times()
        if len(tt) > 0:
            # print( '----------\ntravel time (mean, std) ('+str(np.mean(tt))+', '+str(np.std(tt))+')\n' )
            return [str(int(np.mean(tt))), str(int(np.std(tt)))]
        else:
            return [str(int(0.0)), str(int(0.0))]

    def get_travel_times(self):
        return [self.v_travel_times[v] for v in self.v_travel_times]

    def get_tsc_metrics(self):
        tsc_metrics = {}
        for tsc in self.tsc:
            tsc_metrics[tsc] = self.tsc[tsc].get_traffic_metrics_history()
        return tsc_metrics

    def close(self):
        # self.conn.close()
        self.conn.close()
        self.sumo_process.terminate()
