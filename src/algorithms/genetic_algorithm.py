import random
import copy
import pickle
import numpy as np
from src.generate_data.saveToCsv import write_line_to_file


class GeneticAlgorithm:
    def __init__(self, initial_logic, population_size, mutation_rate, crossover_rate):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.initial_logic = initial_logic if initial_logic else None

    def generate_random_durations(self, traffic_logic):
        for tl, logic in traffic_logic:
            phases = self.filter_phases(logic)
            for phase in phases:
                phase.duration = int(random.uniform(5, 80))
        # print(traffic_logic)
        return traffic_logic

    def generate_initial_population(self, population_size):
        # self.population = [self.mutate(copy.deepcopy(self.initial_logic)) for _ in range(self.population_size)]
        population = []
        for i in range(population_size):
            initial_traffic_logic_copy = copy.deepcopy(self.initial_logic)
            modified_traffic_logic = self.generate_random_durations(
                initial_traffic_logic_copy
            )
            population.append(modified_traffic_logic)
        self.parent_population = population

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
        self.sum_parent_fitness = self.sum_fitness_all(self.parent_fitness)

    def combine_logic_with_fitness(self, logic_list, fitness_values_list):
        sum_fitness_list = fitness_values_list
        self.combined_list = list(zip(logic_list, sum_fitness_list))

    def calculate_probabilities(self, normalized_fitness_list):
        # total_fitness = sum(normalized_fitness_list)
        # probabilities = [fitness / total_fitness for fitness in normalized_fitness_list]
        inverted_fitness_list = [1.0 / fitness for fitness in normalized_fitness_list]
        total_inverted_fitness = sum(inverted_fitness_list)
        probabilities = [
            inverted_fitness / total_inverted_fitness
            for inverted_fitness in inverted_fitness_list
        ]
        write_line_to_file("logs/log.txt", "a", f"PROBABILITIES: {probabilities}")
        # print(probabilities)
        return probabilities

    def roulette_wheel_selection(self):
        logic_list, fitness_list = zip(*self.combined_list)
        probabilities = self.calculate_probabilities(fitness_list)
        selected_index = random.choices(
            range(len(logic_list)), weights=probabilities, k=1
        )[0]
        selected_logic = logic_list[selected_index]
        write_line_to_file("logs/log.txt", "a", f"SELECTED IDX: {selected_index}")
        # write_line_to_file("logs/log.txt", "a", f"SELECTED LOGIC: {selected_logic}")
        return selected_logic

    def tournament_selection(self, tournament_size=5):
        logic_list, fitness_list = zip(*self.combined_list)
        selected_logics = random.choices(logic_list, k=tournament_size)
        # for logic in selected_logics:
        #     write_line_to_file("logs/log.txt", "a", f"SELECTED LOGIC: {logic}")
        # print(logic_list.index(logic))
        selected_fitness = [
            fitness_list[logic_list.index(logic)] for logic in selected_logics
        ]
        selected_index = selected_fitness.index(min(selected_fitness))
        selected_logic = selected_logics[selected_index]
        return selected_logic

    def evaluate_population(self):
        if self.child_population == None:
            self.combine_logic_with_fitness(
                self.parent_population, self.sum_parent_fitness
            )
        #roulette_selected_logic = self.roulette_wheel_selection()
        tournament_selected_logic = self.tournament_selection(tournament_size=5)
        #return roulette_selected_logic
        return tournament_selected_logic

    def generate_average_durations(self, traffic_logic_1, traffic_logic_2):
        for tl, logic in traffic_logic_1:
            for phase_1, phase_2 in zip(phases_1, phases_2):
                phase_1.duration = (phase_1.duration + phase_2.duration) // 2
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

    def crossover(self, parent1, parent2, alpha=0.3):
        if random.random() > self.crossover_rate:
            return self.generate_random_durations(
                parent1
            ), self.generate_random_durations(parent2)

        child1 = []
        child2 = []
        for i in range(len(parent1)):
            tl1, logic1 = parent1[i]
            tl2, logic2 = parent2[i]

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

                phase1.duration = new_duration1
                phase2.duration = new_duration2

                for phase in logic1.phases:
                    if phase in phases1:
                        logic1.phase = phase1
                for phase in logic2.phases:
                    if phase in phases1:
                        logic2.phase = phase1

            child1.append((tl1, logic1))
            child2.append((tl2, logic2))
        return child1, child2

    def mutate(self, traffic_logic):
        for tl, logic in traffic_logic:
            phases = self.filter_phases(logic)
            for phase in phases:
                # if random.random() < self.mutation_rate:
                phase.duration = phase.duration + int(random.uniform(-10, 10))
                if phase.duration < 5:
                    phase.duration = 5
        return traffic_logic

    def generate_children(self):
        population_children = []
        for i in range(0, len(self.parent_population), 2):
            #print(i)
            parent1_logic = self.evaluate_population()
            parent2_logic = self.evaluate_population()
            parent1_logic_copy = copy.deepcopy(parent1_logic)
            parent2_logic_copy = copy.deepcopy(parent2_logic)

            child1_logic, child2_logic = self.crossover(
                parent1_logic_copy, parent2_logic_copy
            )
            if random.random() < self.mutation_rate:
                child1_logic = self.mutate(child1_logic)
            if random.random() < self.mutation_rate:
                child2_logic = self.mutate(child2_logic)

            population_children.append(child1_logic)
            if i + 1 < len(self.parent_population):
                population_children.append(child2_logic)
        self.child_population = population_children
        #print(self.child_population)

    def replace_worst_child_with_best_parent(self):

        best_parent_index = self.sum_parent_fitness.index(min(self.sum_parent_fitness))
        # write_line_to_file(
        #     "logs/log.txt", "a", f"BEST PARENT INDEX: {best_parent_index}"
        # )
        best_parent_logic = self.parent_population[best_parent_index]
        # write_line_to_file(
        #     "logs/log.txt", "a", f"BEST PARENT LOGIC: {best_parent_logic}"
        # )
        best_parent_fitness = self.parent_fitness[best_parent_index]
        # write_line_to_file(
        #     "logs/log.txt", "a", f"BEST PARENT FITNESS: {best_parent_fitness}"
        # )
        sum_child_fitness = self.sum_fitness_all(self.child_fitness)
        # write_line_to_file(
        #     "logs/log.txt", "a", f"SUM CHILD FITNESS: {sum_child_fitness}"
        # )
        worst_child_index = sum_child_fitness.index(max(sum_child_fitness))
        # write_line_to_file(
        #     "logs/log.txt", "a", f"WORST CHILD INDEX: {worst_child_index}"
        # )
        self.child_population[worst_child_index] = best_parent_logic
        self.child_fitness[worst_child_index] = best_parent_fitness
        # write_line_to_file("logs/log.txt", "a", f"AFTER: {self.child_population}")
        # write_line_to_file("logs/log.txt", "a", f"AFTER P: {self.parent_population}")
        return best_parent_index, worst_child_index

    def load_population(self, pickle_file_path):
        with open(pickle_file_path, "rb") as file:
            loaded_data = pickle.load(file)
        results = loaded_data["results"]
        population_idx = loaded_data["population_idx"]
        return results, population_idx
