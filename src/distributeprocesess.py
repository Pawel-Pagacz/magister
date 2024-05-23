import sys, os, subprocess, time
from multiprocessing import *
import numpy as np
from multiprocessing import Process, Manager
from concurrent.futures import ProcessPoolExecutor
from src.sumosimulation import SumoSim
from src.algorithms.genetic_algorithm import GeneticAlgorithm


def get_simulation(simulation):
    if simulation == "wielun":
        net_path = "networks/wielun/wielun.net.xml"
        cfg_path = "networks/wielun/wielun.sumocfg"
    elif simulation == "wroclaw":
        net_path = "networks/wroclaw/wroclaw.net.xml"
        cfg_path = "networks/wroclaw/wroclaw.sumocfg"
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
        self.parent_population = ga.generate_initial_population(self.args.pop_size)

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
        return logic, fitness

    def run(self):
        with ProcessPoolExecutor(max_workers=self.args.n) as executor:
            simulation_result = []
            for i in range(self.args.pop_size):
                logic = self.parent_population[i]
                simulation_result.append(
                    executor.submit(self.simulation, i, self.args, logic)
                )

            results = []
            for future in simulation_result:
                result = future.result()
                results.append(result)

            print(results)
            return results
