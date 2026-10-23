"""
ga/selection.py
---------------
SELECTION - choose parents for the next generation.

We use TOURNAMENT SELECTION:
  1. pick a few random timetables (a "tournament")
  2. the one with the best fitness wins and becomes a parent

Better timetables win more often, but weak ones still have a small chance,
which keeps the population diverse.
"""

import random


def tournament_selection(population, fitness_scores, tournament_size=3):
    """Return the winner of one tournament."""
    size = min(tournament_size, len(population))
    contestants = random.sample(range(len(population)), size)   # random indexes
    winner = max(contestants, key=lambda i: fitness_scores[i])  # best fitness wins
    return population[winner]
