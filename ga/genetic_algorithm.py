"""
ga/genetic_algorithm.py
-----------------------
THE MAIN GENETIC ALGORITHM LOOP

    Population -> Fitness -> Selection -> Crossover -> Mutation
               -> New Population (next Generation) -> Repeat

Includes ELITISM: the best few timetables are copied unchanged into the next
generation, so the best solution found so far is never lost.
"""

import random
import numpy as np

from ga.chromosome import create_lectures, create_population, copy_chromosome
from ga.fitness import calculate_fitness, calculate_penalty
from ga.selection import tournament_selection
from ga.crossover import class_crossover
from ga.mutation import mutate


def evaluate_population(population, problem):
    """FITNESS EVALUATION: give every timetable in the population a score."""
    return [calculate_fitness(chromosome, problem) for chromosome in population]


def run_genetic_algorithm(problem, population_size=100, generations=300,
                          mutation_rate=0.05, crossover_rate=0.8,
                          elite_count=2, seed=None, progress_callback=None):
    """
    Run the GA and return a dictionary with the best timetable and history.
    """
    if seed:                       # same seed -> same result (useful for demo)
        random.seed(seed)
    elite_count = min(elite_count, population_size)

    # ---------- STEP 1: POPULATION INITIALIZATION (generation 0) ----------
    lectures = create_lectures(problem)
    population = create_population(population_size, lectures, problem)

    # ---------- STEP 2: FITNESS EVALUATION ----------
    fitness_scores = evaluate_population(population, problem)

    best_index = int(np.argmax(fitness_scores))
    initial_best = copy_chromosome(population[best_index])   # keep for comparison
    initial_fitness = fitness_scores[best_index]

    # History used for the Generation-vs-Fitness graph
    best_history = [max(fitness_scores)]
    avg_history = [float(np.mean(fitness_scores))]
    penalty_history = [calculate_penalty(population[best_index], problem)]

    # ---------- STEP 3: EVOLVE GENERATION BY GENERATION ----------
    for generation in range(1, generations + 1):

        # ELITISM: copy the best timetables directly into the new population
        ranked = np.argsort(fitness_scores)[::-1]            # best first
        new_population = [copy_chromosome(population[i]) for i in ranked[:elite_count]]

        # Fill the rest of the new population with children
        while len(new_population) < population_size:
            # SELECTION: choose two parents by tournament
            parent1 = tournament_selection(population, fitness_scores)
            parent2 = tournament_selection(population, fitness_scores)

            # CROSSOVER: mix the parents to make two children
            child1, child2 = class_crossover(parent1, parent2, crossover_rate)

            # MUTATION: randomly change a few genes
            mutate(child1, problem, mutation_rate)
            mutate(child2, problem, mutation_rate)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        # NEW GENERATION replaces the old population
        population = new_population
        fitness_scores = evaluate_population(population, problem)

        # Record progress
        best_index = int(np.argmax(fitness_scores))
        best_history.append(fitness_scores[best_index])
        avg_history.append(float(np.mean(fitness_scores)))
        penalty_history.append(calculate_penalty(population[best_index], problem))

        if progress_callback:
            progress_callback(generation, generations, fitness_scores[best_index])

        # Stop early if a perfect timetable (penalty 0) is found
        if penalty_history[-1] == 0:
            break

    # ---------- STEP 4: BEST SOLUTION SELECTION ----------
    best_index = int(np.argmax(fitness_scores))
    return {
        "best_chromosome": population[best_index],
        "best_fitness": fitness_scores[best_index],
        "best_penalty": penalty_history[-1],
        "initial_chromosome": initial_best,
        "initial_fitness": initial_fitness,
        "initial_penalty": penalty_history[0],
        "best_history": best_history,
        "avg_history": avg_history,
        "penalty_history": penalty_history,
        "generations_run": len(best_history) - 1,
    }
