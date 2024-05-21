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

        # def crossover(self, parent1, parent2):
        #     crossover_point = random.randint(1, len(parent1.logic.phases) - 1)

        #     child1_phases = (
        #         parent1.logic.phases[:crossover_point]
        #         + parent2.logic.phases[crossover_point:]
        #     )
        #     child2_phases = (
        #         parent2.logic.phases[:crossover_point]
        #         + parent1.logic.phases[crossover_point:]
        #     )

        #     child1_logic = Logic(
        #         programID=parent1.logic.programID,
        #         type=parent1.logic.type,
        #         currentPhaseIndex=parent1.logic.currentPhaseIndex,
        #         phases=child1_phases,
        #         subParameter=deepcopy(parent1.logic.subParameter),
        #     )

        #     child2_logic = Logic(
        #         programID=parent2.logic.programID,
        #         type=parent2.logic.type,
        #         currentPhaseIndex=parent2.logic.currentPhaseIndex,
        #         phases=child2_phases,
        #         subParameter=deepcopy(parent2.logic.subParameter),
        #     )

        #     child1 = TrafficSignal(signal_id=parent1.signal_id, logic=child1_logic)
        #     child2 = TrafficSignal(signal_id=parent2.signal_id, logic=child2_logic)

        #     return child1, child2

        # def mutate(self, signal):
        #     new_logic = deepcopy(signal.logic)

        #     for phase in new_logic.phases:
        #         if random.random() < self.mutation_rate:
        #             phase = self.generate_random_durations(phase)

        #     return TrafficSignal(signal_id=signal.signal_id, logic=new_logic)

        # def run_simulation(self, signal: TrafficSignal) -> float:

        #     return self.fitness_function(signal)

        # def evaluate_population(self) -> Dict[TrafficSignal, float]:
        #     fitness_results = {}
        #     with ThreadPoolExecutor() as executor:
        #         futures = {
        #             executor.submit(self.run_simulation, signal): signal
        #             for signal in self.population
        #         }
        #         for future in as_completed(futures):
        #             signal = futures[future]
        #             fitness = future.result()
        #             fitness_results[signal] = fitness
        #     return fitness_results

        # def evolve_population(self, fitness_results: Dict[TrafficSignal, float]):
        #     sorted_population = sorted(
        #         fitness_results.keys(), key=lambda x: fitness_results[x], reverse=True
        #     )
        #     new_population = sorted_population[
        #         :2
        #     ]  # Zakładamy, że zawsze zachowujemy najlepsze 2

        #     while len(new_population) < self.population_size:
        #         parent1, parent2 = self.select_parents()
        #         child1, child2 = self.crossover(parent1, parent2)
        #         mutated_child1 = self.mutate(child1)
        #         mutated_child2 = self.mutate(child2)
        #         new_population.extend([mutated_child1, mutated_child2])

        #     self.population = new_population[: self.population_size]

        # def run(self, generations: int):
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
