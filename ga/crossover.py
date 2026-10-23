"""
ga/crossover.py
---------------
CROSSOVER - combine two parent timetables to make two children.

CLASS-WISE CROSSOVER (keeps "no free period" true):
    Parent 1 :  [ CE-A genes | CE-B genes | CE-C genes ]
    Parent 2 :  [ CE-A genes | CE-B genes | CE-C genes ]

    For every class we flip a coin:  child 1 takes that class's whole timetable
    from parent 1 or parent 2, and child 2 takes it from the other parent.

    Child 1  :  [ P1 | P2 | P1 ]
    Child 2  :  [ P2 | P1 | P2 ]

Why whole classes? A class's timetable is a perfect arrangement of its slots
(no free period, no class clash). Copying it as one block keeps it perfect,
while children still inherit good teacher/room combinations from both parents.
(A normal single-point cut could split a class and create empty slots.)

Gene i is always the same lecture in every chromosome, so children are valid.
"""

import random
from ga.chromosome import copy_chromosome


def class_blocks(chromosome):
    """Return {class name: [gene positions]} for a chromosome."""
    blocks = {}
    for index, gene in enumerate(chromosome):
        blocks.setdefault(gene["class"], []).append(index)
    return blocks


def class_crossover(parent1, parent2, crossover_rate):
    """With probability crossover_rate mix the parents, otherwise just copy them."""
    child1 = copy_chromosome(parent1)
    child2 = copy_chromosome(parent2)
    if random.random() < crossover_rate:
        for positions in class_blocks(parent1).values():
            if random.random() < 0.5:                       # swap this class's block
                for i in positions:
                    child1[i] = dict(parent2[i])
                    child2[i] = dict(parent1[i])
    return child1, child2
