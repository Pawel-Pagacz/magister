import sys, os, subprocess, time
from multiprocessing import *
import numpy as np
from multiprocessing import Process, Manager
from concurrent.futures import ProcessPoolExecutor
from src.sumosimulation import SumoSim
from src.algorithms.genetic_algorithm import GeneticAlgorithm
from src.generate_data.saveToCsv import save_to_csv
import math


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
        self.idx = 0

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
        self.ga = GeneticAlgorithm(
            initial_logic=logic,
            population_size=args.n,
            mutation_rate=args.mutation_rate,
        )
        self.parent_population = self.ga.generate_initial_population(self.args.pop_size)

    def simulation(self, i, args, logic):
        sim = SumoSim(
            cfg_path=args.cfg_path,
            steps=args.steps,
            nogui=True,
            args=args,
            idx=i,
            logic=logic,
        )
        self.idx = i
        sim.gen_sim()
        logic, fitness = sim.run()
        save_to_csv(
            logic_data=logic,
            values_data=fitness,
            population=self.population_idx,
            csv_file_path="logic_data.csv",
        )
        return logic, fitness

    def run_simulation(self, population):
        with ProcessPoolExecutor(max_workers=self.args.n) as executor:
            simulation_result = []
            for i in range(self.args.pop_size):
                logic = population[i]
                simulation_result.append(
                    executor.submit(self.simulation, i, self.args, logic)
                )

            results = []
            for future in simulation_result:
                result = future.result()
                results.append(result)

            return results

    def evaluate_population(
        self,
        parent_population,
        parent_fitness,
        child_population=None,
        child_fitness=None,
    ):
        self.ga.update_genetics(
            parent_population=parent_population,
            parent_fitness=parent_fitness,
            child_population=child_population,
            child_fitness=child_fitness,
        )
        self.ga.generate_children()

    def run(self):
        data = self.run_simulation(population=self.parent_population)
        fitness_values = [item[1] for item in data]
        self.evaluate_population(
            parent_population=self.parent_population,
            parent_fitness=fitness_values,
            child_population=None,
            child_fitness=None,
        )
        self.population_idx = 0
        # while self.population_idx < self.args.pop_size:
        #     data = self.run_simulation(population=self.ga.child_population)
        #     fitness_values = [item[1] for item in data]
        #     self.evaluate_population(
        #         parent_population=self.ga.parent_population,
        #         parent_fitness=self.ga.parent_fitness,
        #         child_population=self.ga.child_population,
        #         child_fitness=fitness_values,
        #     )
        #     self.population_idx += 1
