"""
ga/fitness.py
-------------
FITNESS FUNCTION + FITNESS EVALUATION

Step 1: count rule violations in a timetable      -> count_violations()
        (includes the "free period" rule: every slot of every class must be filled)
Step 2: Total Penalty = sum(weight x violations)  -> calculate_penalty()
Step 3: Fitness = 1 / (1 + Total Penalty)         -> calculate_fitness()

Perfect timetable : penalty = 0   -> fitness = 1.0
More conflicts    : penalty grows -> fitness moves towards 0
"""

# Penalty weight for each rule. Hard rules must never be broken -> big weight.
# Soft rules are only "nice to have" -> small weight.
PENALTY_WEIGHTS = {
    "faculty":     10,   # HARD: teacher in two places at the same time
    "class":       10,   # HARD: class has two lectures at the same time
    "room":        10,   # HARD: room used by two lectures at the same time
    "unavailable": 10,   # HARD: teacher scheduled when not available
    "invalid":     10,   # HARD: invalid assignment (room too small / out of range)
    "free":        10,   # HARD: a class has a FREE PERIOD (empty slot)
    "consecutive":  2,   # SOFT: same subject in back-to-back periods
    "gaps":         1,   # SOFT: empty period between two lectures of a class
}

HARD_RULES = ["faculty", "class", "room", "unavailable", "invalid", "free"]
SOFT_RULES = ["consecutive", "gaps"]

RULE_NAMES = {
    "faculty": "Faculty clash",
    "class": "Class clash",
    "room": "Room clash",
    "unavailable": "Teacher unavailable",
    "invalid": "Invalid assignment",
    "free": "Free period (empty slot)",
    "consecutive": "Consecutive same subject",
    "gaps": "Empty period (gap)",
}


def get_unavailable_set(problem):
    """Convert (teacher, 'Friday', 5) into (teacher, day_index, period_index)."""
    result = set()
    for teacher, day_name, period_no in problem["teacher_unavailable"]:
        if day_name in problem["days"]:
            result.add((teacher, problem["days"].index(day_name), int(period_no) - 1))
    return result


def count_violations(chromosome, problem):
    """Count how many times each rule is broken. Returns a dictionary."""
    num_days = len(problem["days"])
    num_periods = problem["num_periods"]
    unavailable = get_unavailable_set(problem)

    teacher_slot = {}   # (teacher, day, period) -> how many lectures
    class_slot = {}     # (class, day, period)   -> list of subjects
    room_slot = {}      # (room, day, period)    -> how many lectures
    invalid = 0
    unavailable_count = 0

    for g in chromosome:
        day, period, room = g["day"], g["period"], g["room"]

        # Invalid assignment: outside the timetable
        if not (0 <= day < num_days and 0 <= period < num_periods):
            invalid += 1
            continue

        # Activity periods (Library, Sports...) need no teacher and no room
        is_activity = g.get("activity", False)
        if not is_activity:
            # Invalid assignment: room too small
            if room not in problem["rooms"] or problem["rooms"][room] < problem["classes"][g["class"]]:
                invalid += 1

            # Teacher not available at this time
            if (g["teacher"], day, period) in unavailable:
                unavailable_count += 1

            t_key = (g["teacher"], day, period)
            r_key = (room, day, period)
            teacher_slot[t_key] = teacher_slot.get(t_key, 0) + 1
            room_slot[r_key] = room_slot.get(r_key, 0) + 1

        # Remember what each class is doing in each slot
        c_key = (g["class"], day, period)
        class_slot.setdefault(c_key, []).append(g["subject"])

    # A slot holding 3 lectures has 2 clashes -> (count - 1)
    faculty = sum(n - 1 for n in teacher_slot.values() if n > 1)
    room_clash = sum(n - 1 for n in room_slot.values() if n > 1)
    class_clash = sum(len(s) - 1 for s in class_slot.values() if len(s) > 1)

    # Soft rule: same subject in two consecutive periods for a class
    consecutive = 0
    for (cls, day, period), subjects in class_slot.items():
        next_subjects = class_slot.get((cls, day, period + 1))
        if next_subjects and set(subjects) & set(next_subjects):
            consecutive += 1

    # Soft rule: empty periods BETWEEN the first and last lecture of a day
    periods_used = {}
    for (cls, day, period) in class_slot:
        periods_used.setdefault((cls, day), []).append(period)
    gaps = 0
    for used in periods_used.values():
        gaps += (max(used) - min(used) + 1) - len(set(used))

    # Hard rule: FREE PERIODS = slots of a class that have no lecture at all
    free = 0
    for class_name in problem["classes"]:
        for d in range(num_days):
            for p in range(num_periods):
                if (class_name, d, p) not in class_slot:
                    free += 1

    return {
        "faculty": faculty,
        "class": class_clash,
        "room": room_clash,
        "unavailable": unavailable_count,
        "invalid": invalid,
        "free": free,
        "consecutive": consecutive,
        "gaps": gaps,
    }


def calculate_penalty(chromosome, problem):
    """Total Penalty = sum of (weight x number of violations)."""
    counts = count_violations(chromosome, problem)
    return sum(PENALTY_WEIGHTS[rule] * counts[rule] for rule in counts)


def calculate_fitness(chromosome, problem):
    """Fitness = 1 / (1 + Total Penalty). Higher is better, maximum is 1."""
    return 1.0 / (1.0 + calculate_penalty(chromosome, problem))


def count_hard_conflicts(counts):
    """Number of hard-rule violations (these are the real 'conflicts')."""
    return sum(counts[rule] for rule in HARD_RULES)


def count_satisfied_constraints(chromosome, problem):
    """
    Every lecture is checked against the 5 hard rules.
    satisfied = total checks - violations found.  Returns (satisfied, total).
    """
    counts = count_violations(chromosome, problem)
    total_checks = len(chromosome) * len(HARD_RULES)
    satisfied = max(0, total_checks - count_hard_conflicts(counts))
    return satisfied, total_checks


def describe_conflicts(chromosome, problem):
    """Human-readable list of hard conflicts (for display in the UI)."""
    days = problem["days"]
    unavailable = get_unavailable_set(problem)
    teacher_slot, room_slot, class_slot = {}, {}, {}
    messages = []

    for g in chromosome:
        key_c = (g["class"], g["day"], g["period"])
        class_slot.setdefault(key_c, []).append(g["subject"])
        if g.get("activity"):
            continue                                  # no teacher / room to check
        key_t = (g["teacher"], g["day"], g["period"])
        key_r = (g["room"], g["day"], g["period"])
        teacher_slot.setdefault(key_t, []).append(g["class"] + "-" + g["subject"])
        room_slot.setdefault(key_r, []).append(g["class"] + "-" + g["subject"])
        if key_t in unavailable:
            messages.append(f"Teacher unavailable: {g['teacher']} on "
                            f"{days[g['day']]} Period {g['period'] + 1}")
        if g["room"] in problem["rooms"] and problem["rooms"][g["room"]] < problem["classes"][g["class"]]:
            messages.append(f"Room too small: {g['room']} for class {g['class']}")

    for (who, d, p), items in teacher_slot.items():
        if len(items) > 1:
            messages.append(f"Faculty clash: {who} on {days[d]} Period {p + 1} -> {', '.join(items)}")
    for (who, d, p), items in room_slot.items():
        if len(items) > 1:
            messages.append(f"Room clash: {who} on {days[d]} Period {p + 1} -> {', '.join(items)}")
    for (who, d, p), items in class_slot.items():
        if len(items) > 1:
            messages.append(f"Class clash: {who} on {days[d]} Period {p + 1} -> {', '.join(items)}")
    for class_name in problem["classes"]:
        for d in range(len(days)):
            for p in range(problem["num_periods"]):
                if (class_name, d, p) not in class_slot:
                    messages.append(f"Free period: {class_name} on {days[d]} Period {p + 1}")
    return messages
