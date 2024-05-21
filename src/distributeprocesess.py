import sys, os, subprocess, time
from multiprocessing import *
import numpy as np
from multiprocessing import Process
from src.sumosimulation import SumoSim
from src.algorithms.genetic_algorithm import GeneticAlgorithm


def get_simulation(simulation):
    if simulation == "wielun":
        net_path = "networks/wielun/wielun.net.xml"
        cfg_path = "networks/wielun/wielun.sumocfg"
    elif simulation == "wroclaw":
        net_path = "networks/wroclaw/wroclaw.net.xml"
        cfg_path = "networks/wroclaw/wroclaw.sumocfg"
        print(net_path, cfg_path)
    else:
        raise ValueError(f"Unknown simulation: {simulation}")

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
            args.cfg_path, args.net_path = get_simulation(args.simulation)

        dummy_sim = SumoSim(
            cfg_path=args.cfg_path,
            steps=args.steps,
            nogui=True,
            args=args,
            idx=-1,
        )
        logic, _ = dummy_sim.gen_sim()
        print(logic)
        ga = GeneticAlgorithm(
            initial_logic=logic,
            population_size=args.n,
            mutation_rate=args.mutation_rate,
        )
        self.population = ga.generate_initial_population(self.procs)

    def simulation(self, i, args, logic):
        sim = SumoSim(
            cfg_path=args.cfg_path,
            steps=args.steps,
            nogui=True,
            args=args,
            idx=i,
            logic=logic,
        )
        sim.gen_sim()
        logic, fitness = sim.run()
        print(logic, fitness)

    def run(self):
        processes = []
        for i in range(self.procs):
            logic = self.population[i]
            p = Process(target=self.simulation, args=(i, self.args, logic))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()

    # with Pool(processes=args.n) as pool:
    #     sims = [
    #         SumoSim(
    #             cfg_path=args.cfg_path,
    #             steps=args.steps,
    #             algorithm=args.algorithm,
    #             nogui=True,
    #             args=args,
    #             idx=i,
    #             logic=initial_population,
    #         )
    #         for i in range(args.n)
    #     ]
    #     pool.map(SumoSim.gen_and_run, sims)

    # print(logic, fitness)
    # new_sim = SumoSim(
    #     cfg_path=args.cfg_path,
    #     steps=args.steps,
    #     algorithm=args.algorithm,
    #     nogui=True,
    #     args=args,
    #     idx=0,
    #     logic=logic,
    # )
    # new_sim.gen_sim()
    # logic, fitness = new_sim.run()
    # print(logic, fitness)
