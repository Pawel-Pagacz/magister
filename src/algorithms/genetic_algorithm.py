import random
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict
from collections import namedtuple
import copy
import pandas as pd
import pickle


class Logic:
    def __init__(self, programID, type, currentPhaseIndex, phases, subParameter):
        self.programID = programID
        self.type = type
        self.currentPhaseIndex = currentPhaseIndex
        self.phases = phases
        self.subParameter = subParameter


class GeneticAlgorithm:
    def __init__(
        self,
        initial_logic,
        population_size,
        mutation_rate,
        crossover_rate,
        parent_population=None,
        child_population=None,
        parent_fitness=None,
        child_fitness=None,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.parent_population = parent_population if parent_population else None
        self.child_population = child_population if child_population else None
        self.parent_fitness = parent_fitness if parent_fitness else None
        self.child_fitness = child_fitness if child_fitness else None
        self.initial_logic = initial_logic if initial_logic else None

    def generate_random_durations(self, traffic_logic):
        for tl, logic in traffic_logic:
            phases = self.filter_phases(logic)
            for phase in phases:
                phase.duration = int(random.uniform(5, 80))
                phase.minDur = int(random.uniform(3, 10))
                phase.maxDur = int(random.uniform(phase.duration, 100))
        return traffic_logic

    def generate_initial_population(self, population_size):
        population = []
        for i in range(population_size):
            initial_traffic_logic_copy = copy.deepcopy(self.initial_logic)
            modified_traffic_logic = self.generate_random_durations(
                initial_traffic_logic_copy
            )
            population.append(modified_traffic_logic)
        return population

    def filter_phases(self, logic):
        filtered_phases = [
            phase for phase in logic.phases if "G" in phase.state or "g" in phase.state
        ]
        return filtered_phases

    def sum_fitness_all(self, fitness_values_list):
        sum_fitness_list = [
            (
                sum(fitness_values.values())
                if isinstance(fitness_values, dict)
                else fitness_values
            )
            for fitness_values in fitness_values_list
        ]
        return sum_fitness_list

    def update_genetics(
        self, parent_population, child_population, parent_fitness, child_fitness
    ):
        self.parent_population = parent_population
        self.child_population = child_population
        self.parent_fitness = parent_fitness
        self.child_fitness = child_fitness

    def combine_logic_with_fitness(self, logic_list, fitness_values_list):
        sum_fitness_list = self.sum_fitness_all(fitness_values_list)
        combined_list = list(zip(logic_list, sum_fitness_list))
        return combined_list

    def calculate_probabilities(self, normalized_fitness_list):
        total_fitness = sum(normalized_fitness_list)
        probabilities = [fitness / total_fitness for fitness in normalized_fitness_list]
        return probabilities

    def roulette_wheel_selection(self, combined_list):
        logic_list, fitness_list = zip(*combined_list)
        probabilities = self.calculate_probabilities(fitness_list)
        selected_index = random.choices(
            range(len(logic_list)), weights=probabilities, k=1
        )[0]
        selected_logic = logic_list[selected_index]
        return selected_logic

    def evaluate_population(self):
        sum_parent_fitness = self.sum_fitness_all(self.parent_fitness)
        combined_parent = self.combine_logic_with_fitness(
            self.parent_population, sum_parent_fitness
        )
        combined_list = combined_parent
        if not self.child_population:
            roulette_selected_logic = self.roulette_wheel_selection(
                combined_list=combined_list
            )
        return roulette_selected_logic

    def generate_average_durations(self, traffic_logic_1, traffic_logic_2):
        for tl, logic in traffic_logic_1:
            for phase_1, phase_2 in zip(phases_1, phases_2):
                phase_1.duration = (phase_1.duration + phase_2.duration) // 2
                phase_1.minDur = (phase_1.minDur + phase_2.minDur) // 2
                phase_1.maxDur = (phase_1.maxDur + phase_2.maxDur) // 2
        return traffic_logic_1

    # def crossover(self, parent1, parent2):
    #     child1, child2 = [], []
    #     if random.random() > self.crossover_rate:
    #         return self.generate_random_durations(
    #             parent1
    #         ), self.generate_random_durations(parent2)
    #     for i in range(len(parent1)):
    #         if i % 2 == 0:
    #             child1.append(parent1[i])
    #             child2.append(parent2[i])

    #         else:
    #             child1.append(parent2[i])
    #             child2.append(parent1[i])
    #     return child1, child2

    def crossover(self, parent1, parent2, alpha=0.5):
        if random.random() > self.crossover_rate:
            return self.generate_random_durations(
                parent1
            ), self.generate_random_durations(parent2)
        for i in range(len(parent1)):
            tl1, logic1 = parent1[i]
            tl2, logic2 = parent2[i]
            child_logic1 = []
            child_logic2 = []

            phases1 = self.filter_phases(logic1)
            phases2 = self.filter_phases(logic2)

            for phase1, phase2 in zip(phases1, phases2):
                duration1 = phase1.duration
                duration2 = phase2.duration
                d = abs(duration1 - duration2)
                lower_bound = min(duration1, duration2) - alpha * d
                upper_bound = max(duration1, duration2) + alpha * d

                new_duration1 = int(random.uniform(lower_bound, upper_bound))
                new_duration2 = int(random.uniform(lower_bound, upper_bound))

                new_minDur1 = int(random.uniform(3, min(10, new_duration1)))
                new_maxDur1 = int(random.uniform(new_duration1, 100))

                new_minDur2 = int(random.uniform(3, min(10, new_duration2)))
                new_maxDur2 = int(random.uniform(new_duration2, 100))

                phase1.duration = new_duration1
                phase1.minDur = new_minDur1
                phase1.maxDur = new_maxDur1
                phase2.duration = new_duration2
                phase2.minDur = new_minDur2
                phase2.maxDur = new_maxDur2
        # print(parent1, parent2)
        return parent1, parent2

    def mutate(self, traffic_logic):
        for tl, logic in traffic_logic:
            phases = self.filter_phases(logic)
            for phase in phases:
                if random.random() < self.mutation_rate:
                    phase.duration = phase.duration + int(random.uniform(-10, 10))
                    phase.minDur = phase.minDur + int(random.uniform(-5, 5))
                    phase.maxDur = phase.maxDur + int(random.uniform(-10, 10))
                    if phase.duration < 5:
                        phase.duration = 5
                    if phase.minDur < 3:
                        phase.minDur = 3
                    if phase.maxDur < phase.duration:
                        phase.maxDur = phase.duration + 5
                    if phase.maxDur > 100:
                        phase.maxDur = 100
        return traffic_logic

    def generate_children(self):
        population_children = [None] * len(self.parent_population)
        for i in range(0, len(self.parent_population), 2):

            parent1_logic = self.evaluate_population()
            parent2_logic = self.evaluate_population()

            child1_logic, child2_logic = self.crossover(parent1_logic, parent2_logic)
            child1_logic = self.mutate(child1_logic)
            child2_logic = self.mutate(child2_logic)

            population_children[i] = child1_logic
            population_children[i + 1] = (
                child2_logic if i + 1 < len(self.parent_population) else None
            )
        self.child_population = population_children

    def replace_worst_child_with_best_parent(self):
        # print("BEFORE:", self.child_population)
        sum_parent_fitness = self.sum_fitness_all(self.parent_fitness)
        # print(sum_parent_fitness)
        best_parent_index = sum_parent_fitness.index(min(sum_parent_fitness))
        # print(best_parent_index)
        best_parent_logic = self.parent_population[best_parent_index]
        # print(best_parent_logic)
        best_parent_fitness = self.parent_fitness[best_parent_index]
        # print(best_parent_fitness)
        sum_child_fitness = self.sum_fitness_all(self.child_fitness)
        # print(sum_child_fitness)
        worst_child_index = sum_child_fitness.index(max(sum_child_fitness))
        # print(worst_child_index)
        self.child_population[worst_child_index] = best_parent_logic
        self.child_fitness[worst_child_index] = best_parent_fitness
        # print("AFTER:", self.child_population)

    def load_population(self, pickle_file_path):
        with open(pickle_file_path, "rb") as file:
            loaded_data = pickle.load(file)
        results = loaded_data["results"]
        population_idx = loaded_data["population_idx"]
        return results, population_idx
