import random
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict


class Phase:
    def __init__(self, duration: float, state: str, minDur: float, maxDur: float):
        self.duration = duration
        self.state = state
        self.minDur = minDur
        self.maxDur = maxDur


class Logic:
    def __init__(
        self,
        programID: str,
        type: int,
        currentPhaseIndex: int,
        phases: Tuple[Phase, ...],
        subParameter: dict,
    ):
        self.programID = programID
        self.type = type
        self.currentPhaseIndex = currentPhaseIndex
        self.phases = phases
        self.subParameter = subParameter


class TrafficSignal:
    def __init__(self, signal_id: str, logic: Logic):
        self.signal_id = signal_id
        self.logic = logic


class GeneticAlgorithm:
    def __init__(
        self,
        initial_logic: Logic,
        population_size: int,
        mutation_rate: float,
        fitness_function,
    ):
        self.initial_logic = initial_logic
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.fitness_function = fitness_function
        self.population = self.generate_initial_population(population_size)

    def generate_random_durations(self, phase: Phase) -> Phase:
        phase.duration = random.uniform(5, 80)
        phase.minDur = random.uniform(0, 10)
        phase.duration = random.uniform(30, 100)
        return phase

    def filter_phases(self, traffic_light_logistic):
        filtered_genotype = []
        for tl_id, logic in traffic_light_logistic:
            filtered_phases = [
                phase
                for phase in logic.phases
                if "G" in phase.state or "g" in phase.state
            ]
            if filtered_phases:
                filtered_genotype.append(
                    (
                        tl_id,
                        Logic(
                            programID=logic.programID,
                            type=logic.type,
                            currentPhaseIndex=logic.currentPhaseIndex,
                            phases=tuple(filtered_phases),
                            subParameter=logic.subParameter,
                        ),
                    )
                )
        return filtered_genotype

    def generate_initial_population(self, population_size: int) -> List[TrafficSignal]:
        initial_phases = self.initial_logic.phases
        population = []

        for i in range(population_size):
            phases = deepcopy(initial_phases)
            for phase in phases:

                phase = self.generate_random_durations(phase)
            logic = Logic(
                programID=self.initial_logic.programID,
                type=self.initial_logic.type,
                currentPhaseIndex=self.initial_logic.currentPhaseIndex,
                phases=phases,
                subParameter=deepcopy(self.initial_logic.subParameter),
            )
            population.append(TrafficSignal(signal_id=f"signal_{i}", logic=logic))
        return population

    def select_parents(self) -> Tuple[TrafficSignal, TrafficSignal]:
        return random.sample(self.population, 2)

    def crossover(
        self, parent1: TrafficSignal, parent2: TrafficSignal
    ) -> Tuple[TrafficSignal, TrafficSignal]:
        crossover_point = random.randint(1, len(parent1.logic.phases) - 1)

        child1_phases = (
            parent1.logic.phases[:crossover_point]
            + parent2.logic.phases[crossover_point:]
        )
        child2_phases = (
            parent2.logic.phases[:crossover_point]
            + parent1.logic.phases[crossover_point:]
        )

        child1_logic = Logic(
            programID=parent1.logic.programID,
            type=parent1.logic.type,
            currentPhaseIndex=parent1.logic.currentPhaseIndex,
            phases=child1_phases,
            subParameter=deepcopy(parent1.logic.subParameter),
        )

        child2_logic = Logic(
            programID=parent2.logic.programID,
            type=parent2.logic.type,
            currentPhaseIndex=parent2.logic.currentPhaseIndex,
            phases=child2_phases,
            subParameter=deepcopy(parent2.logic.subParameter),
        )

        child1 = TrafficSignal(signal_id=parent1.signal_id, logic=child1_logic)
        child2 = TrafficSignal(signal_id=parent2.signal_id, logic=child2_logic)

        return child1, child2

    def mutate(self, signal: TrafficSignal) -> TrafficSignal:
        new_logic = deepcopy(signal.logic)

        for phase in new_logic.phases:
            if random.random() < self.mutation_rate:
                phase = self.generate_random_durations(phase)

        return TrafficSignal(signal_id=signal.signal_id, logic=new_logic)

    def run_simulation(self, signal: TrafficSignal) -> float:
        return self.fitness_function(signal)

    def evaluate_population(self) -> Dict[TrafficSignal, float]:
        fitness_results = {}
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.run_simulation, signal): signal
                for signal in self.population
            }
            for future in as_completed(futures):
                signal = futures[future]
                fitness = future.result()
                fitness_results[signal] = fitness
        return fitness_results

    def evolve_population(self, fitness_results: Dict[TrafficSignal, float]):
        sorted_population = sorted(
            fitness_results.keys(), key=lambda x: fitness_results[x], reverse=True
        )
        new_population = sorted_population[
            :2
        ]  # Zakładamy, że zawsze zachowujemy najlepsze 2

        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents()
            child1, child2 = self.crossover(parent1, parent2)
            mutated_child1 = self.mutate(child1)
            mutated_child2 = self.mutate(child2)
            new_population.extend([mutated_child1, mutated_child2])

        self.population = new_population[: self.population_size]

    def run(self, generations: int):
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
