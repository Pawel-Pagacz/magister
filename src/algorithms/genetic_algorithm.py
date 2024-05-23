import random
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict
from collections import namedtuple
import copy

# class Phase:
#     def __init__(self, duration: float, state: str, minDur: float, maxDur: float):
#         self.duration = duration
#         self.state = state
#         self.minDur = minDur
#         self.maxDur = maxDur


class Logic:
    def __init__(
        self,
        programID,
        type,
        currentPhaseIndex,
        phases,
        subParameter,
    ):
        self.programID = programID
        self.type = type
        self.currentPhaseIndex = currentPhaseIndex
        self.phases = phases
        self.subParameter = subParameter


class TrafficSignal:
    def __init__(self, signal_id: str, logic):
        self.signal_id = signal_id
        self.logic = logic


Phase = namedtuple("Phase", ["duration", "state", "minDur", "maxDur"])
# Logic = namedtuple(
#     "Logic", ["programID", "type", "currentPhaseIndex", "phases", "subParameter"]
# )
TrafficSignal = namedtuple("TrafficSignal", ["signal_id", "logic"])


class GeneticAlgorithm:
    def __init__(
        self,
        initial_logic,
        population_size,
        mutation_rate,
        population=None,
    ):
        self.initial_logic = initial_logic
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = population if population else 0

    def generate_random_durations(self, traffic_logic):
        for tl, logic in traffic_logic:
            phases = self.filter_phases(logic)
            for phase in phases:
                phase.duration = int(random.uniform(5, 80))
                phase.minDur = int(random.uniform(3, phase.duration))
                phase.maxDur = int(random.uniform(phase.duration, 100))
        # print("Random durations: ", traffic_logic)
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

    def select_parents(self):
        return random.sample(self.population, 2)

    def get_population(self):
        return self.population

        #     return self.fitness_function(signal)

    def evaluate_population(self, children_population):
        evaluated_population = [
            (logic, fitness_scores[tl]) for tl, logic in logic_fitness_pairs
        ]
        print(evaluated_population)

        for generation in range(generations):
            print(f"Generation {generation+1}")
            fitness_results = self.evaluate_population()
            self.evolve_population(fitness_results)
            # Wyświetlanie wyników
            best_signal = max(fitness_results, key=fitness_results.get)
            print(f"Best fitness: {fitness_results[best_signal]}")
            print(
                f"Best signal phases: {[phase.state for phase in best_signal.logic.phases]}"
            )
