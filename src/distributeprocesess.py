import sys, os, subprocess, time
from multiprocessing import *
import numpy as np

from src.sumosimulation import SumoSim


def get_simulation(simulation):

    if simulation == "wielun":
        net_path = "networks/wielun/wielun.net.xml"
        cfg_path = "networks/wielun/wielun.sumocfg"
    elif simulation == "wroclaw":
        net_fp = "networks/wroclaw/wroclaw.net.xml"
        cfg_fp = "networks/wroclaw/wroclaw.sumocfg"
    return cfg_path, net_path


class DistributeProcesses:
    def __init__(self, args, algorithm):
        self.args = args
        self.procs = args.n
        algorithms = ["GA"]

        if algorithm not in algorithms:
            print(
                "Selected Traffic Light Scheduling Algoritm "
                + str(algorithm)
                + " not found, please provide valid algorithm."
            )
            return

        if args.n < 0:
            print("Number of processes cannot be less than 0. Setting to 1.")
            args.n = 1

        if args.simulation:
            args.cfg_path, args.net_path = get_simulation(args.sim)

        sim = SumoSim(args.cfg_path, args.steps, args.algorithm, True, args, -1)
        sim.gen_sim()
        sim.run()
