import sys, os, subprocess, time
from multiprocessing import *
import numpy as np

from src.network import Network


def get_simulation(simulation):
    # get simulation
    if simulation == "wielun":
        net_path = "networks/wielun/wielun.net.xml"
        cfg_path = "networks/wielun/wielun.sumocfg"
    # elif simulation == "wroclaw":
    #     net_fp = "networks/wroclaw/wroclaw.net.xml"
    #     cfg_fp = "networks/wroclaw/wroclaw.sumocfg"
    return cfg_path, net_path


class DistributeProcesses:
    def __init__(self, args, method):
        self.args = args
        algorithms = ["GA"]

    if algorithm in algorithms:
        pass
    else:
        print(
            "Selected Traffic Light Scheduling Algoritm "
            + str(algorithm)
            + " not found, please provide valid algorithm."
        )
        return

    if args.n < 0:
        args.n = 1

    if args.simulation:
        args.cfg_path, args.net_path = get_simulation(args.sim)

    # Barrier class from multiprocessing - number of threads that need to wait for each other
    barrier = Barrier(args.n)

    net = Network(args.net_path)
    network = net.get_net_data()
