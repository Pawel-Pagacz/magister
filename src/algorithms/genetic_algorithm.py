import random
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict
from collections import namedtuple
import copy


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
        parent_population=None,
        child_population=None,
        parent_fitness=None,
        child_fitness=None,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.parent_population = parent_population if parent_population else None
        self.child_population = child_population if child_population else None
        self.parent_fitness = parent_fitness if parent_fitness else None
        self.child_fitness = child_fitness if child_fitness else None
        self.initial_logic = initial_logic if initial_logic else None

    def generate_random_durations(self, traffic_logic):
        for tl, logic in traffic_logic:
            # print(logic)
            phases = self.filter_phases(logic)
            for phase in phases:
                phase.duration = int(random.uniform(5, 80))
                phase.minDur = int(random.uniform(3, phase.duration))
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
        self.parent_population = population
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
        print(selected_index)
        print(probabilities)
        selected_logic = logic_list[selected_index]
        return selected_logic

    def evaluate_population(self):
        sum_parent_fitness = self.sum_fitness_all(self.parent_fitness)
        combined_parent = self.combine_logic_with_fitness(
            self.parent_population, sum_parent_fitness
        )
        if self.child_population:
            sum_child_fitness = self.sum_fitness_all(self.child_fitness)
            combined_child = self.combine_logic_with_fitness(
                self.child_population, sum_child_fitness
            )
            combined_list = combined_parent + combined_child
        else:
            combined_list = combined_parent

        combined_list.sort(key=lambda x: x[1])
        self.best_logic = combined_list[0][0]

        roulette_selected_logic = self.roulette_wheel_selection(
            combined_list=combined_list[1:]
        )
        selected_logic_fitness = [
            logic_fitness[1]
            for logic_fitness in combined_list
            if logic_fitness[0] in roulette_selected_logic
        ]
        print("Best Logic:", self.best_logic)
        print("Roulette Logic:", roulette_selected_logic)
        return roulette_selected_logic, selected_logic_fitness

    def crossover(self, parent1, parent2):
        print("P1 - ", parent1, "P2 - ", parent2)
        child1, child2 = [], []
        for i in range(len(parent1)):
            if i % 3 == 0:
                child1.append(parent1[i])
                child2.append(parent2[i])

            else:
                child1.append(parent2[i])
                child2.append(parent1[i])

        print("C1 - ", child1, "C2 - ", child2)
        return child1, child2

    def mutate(self, traffic_logic):
        for tl, logic in traffic_logic:
            phases = self.filter_phases(logic)
            for phase in phases:
                phase.duration = phase.duration + int(random.uniform(-20, 20))
                phase.minDur = phase.minDur + int(random.uniform(-10, 10))
                phase.maxDur = phase.maxDur + int(random.uniform(-10, 10))
        return traffic_logic

    def generate_children(self):
        population_children = len(self.parent_population) * [None]
        for i in range(0, len(self.parent_population), 2):

            parent1_logic, parent1_fitness = self.evaluate_population()
            parent2_logic, parent2_fitness = self.evaluate_population()

            child1_logic, child2_logic = self.crossover(parent1_logic, parent2_logic)

            population_children[i] = child1_logic
            population_children[i + 1] = (
                child2_logic if i + 1 < len(self.parent_population) else None
            )
