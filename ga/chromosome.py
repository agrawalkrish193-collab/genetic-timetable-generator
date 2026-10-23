"""
ga/chromosome.py
----------------
CHROMOSOME REPRESENTATION + POPULATION INITIALIZATION

GENE        = one lecture placed in the timetable. A gene is a small dictionary:
              {"class": "CE-A", "subject": "DBMS", "teacher": "Prof. Sharma",
               "day": 2, "period": 3, "room": "R101"}
              (class/subject/teacher are FIXED by the input,
               day/period/room are what the GA searches for)

CHROMOSOME  = a list of ALL genes = one complete timetable for all classes.

POPULATION  = a list of many chromosomes (many different timetables).

Important design points
-----------------------
1. Gene number i always represents the SAME lecture in every chromosome.

2. NO FREE PERIOD GUARANTEE:
   Every class has exactly (days x periods) lectures, and the lectures of one
   class are always placed on DIFFERENT slots (a random permutation of the
   slots). So every slot of every class is filled - no free period is possible.
   Crossover and mutation only ever swap lectures inside a class, so this
   property is never broken.

3. Optional "activity" lectures (Library, Sports...) can fill leftover slots
   when the subjects alone do not add up to the full week. They need no teacher
   and no room, and are marked with  "activity": True.
"""

import random


def create_lectures(problem):
    """
    Make the list of lectures that must be scheduled.
    E.g. CE-A has DBMS 4 times -> 4 lectures of (CE-A, DBMS, Prof. Sharma).
    """
    lectures = []
    total_slots = len(problem["days"]) * problem["num_periods"]
    activities = problem.get("activities", [])

    for class_name in problem["classes"]:
        count = 0
        for subject in problem["subjects"]:
            for _ in range(subject["lectures"]):
                lectures.append({
                    "class": class_name,
                    "subject": subject["name"],
                    "teacher": subject["teacher"],
                })
                count += 1

        # Fill any leftover slots with activity periods (only if enabled)
        i = 0
        while activities and count < total_slots:
            lectures.append({
                "class": class_name,
                "subject": activities[i % len(activities)],
                "teacher": "",
                "activity": True,
            })
            count += 1
            i += 1
    return lectures


def create_chromosome(lectures, problem):
    """
    One random timetable.
    For every class: shuffle all its slots and hand one slot to each lecture.
    -> no two lectures of a class share a slot, and no slot stays empty.
    """
    num_days = len(problem["days"])
    num_periods = problem["num_periods"]
    all_slots = [(d, p) for d in range(num_days) for p in range(num_periods)]
    room_names = list(problem["rooms"].keys())

    # Group the lecture positions by class
    positions = {}
    for index, lecture in enumerate(lectures):
        positions.setdefault(lecture["class"], []).append(index)

    chromosome = [None] * len(lectures)
    for class_name, idx_list in positions.items():
        slots = all_slots[:]
        random.shuffle(slots)
        for position, (day, period) in zip(idx_list, slots):
            gene = dict(lectures[position])                 # copy fixed part
            gene["day"], gene["period"] = day, period
            gene["room"] = "-" if gene.get("activity") else random.choice(room_names)
            chromosome[position] = gene
    return chromosome


def create_population(population_size, lectures, problem):
    """POPULATION INITIALIZATION: many random timetables."""
    return [create_chromosome(lectures, problem) for _ in range(population_size)]


def copy_chromosome(chromosome):
    """Make an independent copy (so changing a child never changes a parent)."""
    return [dict(gene) for gene in chromosome]
