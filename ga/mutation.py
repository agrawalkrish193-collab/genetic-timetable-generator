"""
ga/mutation.py
--------------
MUTATION - small random changes that add NEW variety.

Each gene is mutated with probability = mutation_rate.
GUIDED MUTATION: a lecture that is currently CLASHING (teacher / room clash or
teacher not available) is
  1. mutated much more often (CONFLICT_RATE) than a lecture that is already fine
     (lectures of the same subject in back-to-back periods get a smaller boost, SOFT_RATE)
  2. swapped with a partner that actually fixes the clash when one exists
     (both teachers are free in each other's slot), otherwise a random partner.
This spends the random changes where they are needed.

A mutated gene does ONE of:

  * SWAP  (70%): swap the (day, period) of this lecture with another lecture of
                 the SAME class. Because two lectures just trade places, every
                 slot stays filled -> a free period can never appear.
  * ROOM  (30%): move the lecture to another random room.
                 (Activity periods have no room, so they only swap.)
"""

import random
from ga.fitness import get_unavailable_set

CONFLICT_RATE = 0.30      # mutation chance for a lecture that is clashing
SOFT_RATE = 0.15          # mutation chance for a lecture repeated in back-to-back periods


def find_conflicting_genes(chromosome, problem, unavailable):
    """Return the set of gene positions that take part in a teacher/room clash."""
    teacher_slot, room_slot, bad = {}, {}, set()
    for i, g in enumerate(chromosome):
        if g.get("activity"):
            continue
        t_key = (g["teacher"], g["day"], g["period"])
        r_key = (g["room"], g["day"], g["period"])
        teacher_slot.setdefault(t_key, []).append(i)
        room_slot.setdefault(r_key, []).append(i)
        if t_key in unavailable:
            bad.add(i)
        if problem["rooms"].get(g["room"], 0) < problem["classes"][g["class"]]:
            bad.add(i)                                   # room too small
    for members in list(teacher_slot.values()) + list(room_slot.values()):
        if len(members) > 1:
            bad.update(members)
    return bad


def find_back_to_back_genes(chromosome):
    """Positions of lectures whose subject is repeated in the next/previous period (soft rule)."""
    subject_at = {(g["class"], g["day"], g["period"]): g["subject"] for g in chromosome}
    soft = set()
    for i, g in enumerate(chromosome):
        for neighbour in (g["period"] - 1, g["period"] + 1):
            if subject_at.get((g["class"], g["day"], neighbour)) == g["subject"]:
                soft.add(i)
    return soft


def pick_swap_partner(i, chromosome, class_positions, teacher_busy, unavailable):
    """
    Choose which lecture of the same class gene i should swap places with.
    Prefer a partner whose swap puts BOTH teachers in a free, available slot.
    """
    gi = chromosome[i]
    candidates = random.sample(class_positions, min(8, len(class_positions)))
    for j in candidates:
        gj = chromosome[j]
        if j == i or gi["teacher"] == gj["teacher"]:
            continue
        ok = True
        if not gi.get("activity"):          # gi moves to gj's slot
            slot = (gi["teacher"], gj["day"], gj["period"])
            ok = teacher_busy.get(slot, 0) == 0 and slot not in unavailable
        if ok and not gj.get("activity"):   # gj moves to gi's slot
            slot = (gj["teacher"], gi["day"], gi["period"])
            ok = teacher_busy.get(slot, 0) == 0 and slot not in unavailable
        if ok:
            return j
    return random.choice(class_positions)   # no perfect partner: random one


def mutate(chromosome, problem, mutation_rate):
    """Mutate a chromosome in place and return it."""
    room_names = list(problem["rooms"].keys())
    unavailable = get_unavailable_set(problem)
    conflicting = find_conflicting_genes(chromosome, problem, unavailable)
    back_to_back = find_back_to_back_genes(chromosome)

    # How many lectures each teacher has in each slot (used to find free slots)
    teacher_busy = {}
    for g in chromosome:
        if not g.get("activity"):
            key = (g["teacher"], g["day"], g["period"])
            teacher_busy[key] = teacher_busy.get(key, 0) + 1

    # Positions of every class's lectures (needed to pick a swap partner)
    positions = {}
    for index, gene in enumerate(chromosome):
        positions.setdefault(gene["class"], []).append(index)

    for i, gene in enumerate(chromosome):
        if i in conflicting:
            rate = CONFLICT_RATE
        elif i in back_to_back:
            rate = SOFT_RATE
        else:
            rate = mutation_rate
        if random.random() >= rate:
            continue
        if gene.get("activity") or random.random() < 0.7:
            if i in conflicting and not gene.get("activity"):
                j = pick_swap_partner(i, chromosome, positions[gene["class"]],
                                      teacher_busy, unavailable)
            else:
                j = random.choice(positions[gene["class"]])  # partner in same class
            other = chromosome[j]
            gene["day"], other["day"] = other["day"], gene["day"]
            gene["period"], other["period"] = other["period"], gene["period"]
        else:
            gene["room"] = random.choice(room_names)
    return chromosome
