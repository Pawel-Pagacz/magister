import numpy as np


class GeneticAlgorithm:
    def __init__(
        self, pop_size, chromosome_length, generations, tournament_size, mutation_rate
    ):
        self.pop_size = pop_size
        self.chromosome_length = chromosome_length
        self.generations = generations
        self.tournament_size = tournament_size
        self.mutation_rate = mutation_rate

    def fitness_function(self, x):
        return np.sum(x)

    def initialize_population(self):
        return np.random.randint(2, size=(self.pop_size, self.chromosome_length))

    def tournament_selection(self, population, fitness_values):
        selected_indices = []
        for _ in range(self.pop_size):
            tournament_indices = np.random.choice(
                self.pop_size, self.tournament_size, replace=False
            )
            tournament_fitness = fitness_values[tournament_indices]
            winner_index = tournament_indices[np.argmax(tournament_fitness)]
            selected_indices.append(winner_index)
        return population[selected_indices]

    def crossover(self, parent1, parent2):
        crossover_point = np.random.randint(1, len(parent1))
        child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
        child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
        return child1, child2

    def mutate(self, individual):
        for i in range(len(individual)):
            if np.random.rand() < self.mutation_rate:
                individual[i] = 1 - individual[i]
        return individual

    def evolve(self):
        population = self.initialize_population()
        for _ in range(self.generations):
            fitness_values = np.array(
                [self.fitness_function(individual) for individual in population]
            )
            selected_parents = self.tournament_selection(population, fitness_values)
            offspring = []
            for i in range(0, self.pop_size, 2):
                child1, child2 = self.crossover(
                    selected_parents[i], selected_parents[i + 1]
                )
                offspring.extend([child1, child2])
            mutated_offspring = [self.mutate(individual) for individual in offspring]
            population = np.array(mutated_offspring)
        final_fitness = np.array(
            [self.fitness_function(individual) for individual in population]
        )
        best_solution_index = np.argmax(final_fitness)
        best_solution = population[best_solution_index]
        best_fitness = final_fitness[best_solution_index]
        return best_solution, best_fitness


# Użycie klasy GeneticAlgorithm
pop_size = 50
chromosome_length = 10
generations = 100
tournament_size = 5
mutation_rate = 0.01

ga = GeneticAlgorithm(
    pop_size, chromosome_length, generations, tournament_size, mutation_rate
)
best_solution, best_fitness = ga.evolve()

print("Najlepsze rozwiązanie:", best_solution)
print("Wartość funkcji przystosowania dla najlepszego rozwiązania:", best_fitness)
