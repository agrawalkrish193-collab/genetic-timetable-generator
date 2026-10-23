# AI-Based College Timetable Generator Using Genetic Algorithm

## 1. Project Title
**AI-Based College Timetable Generator Using Genetic Algorithm** (AISC – Artificial Intelligence and Soft Computing)

## 2. Introduction
Making a college timetable by hand is slow and error-prone. This project uses a **Genetic Algorithm (GA)**, an AI technique inspired by natural evolution, to generate a timetable automatically. The GA is implemented from scratch in Python (no optimization library) and shown through a modern Streamlit web interface.

## 3. Problem Statement
Given classes, subjects, teachers, rooms, working days and periods, place every lecture in a (day, period, room) slot so that there are no clashes and **no free period** (every period of every class has a lecture). The number of possible timetables is astronomically large, so trying them all is impossible.

## 4. Objective
- Generate a clash-free timetable automatically using a Genetic Algorithm.
- **Leave no free period:** every class has a lecture in every period.
- Minimize faculty and room clashes and repeated consecutive subjects.
- Show the improvement visually (Generation vs Fitness graph).

## 5. Why Genetic Algorithm?
Timetabling is a combinatorial optimization problem with many constraints. A GA does not need to try every possibility: it starts from random solutions and improves them step by step, and it works well when a "good enough" solution is acceptable.

## 6. Technologies Used
Python 3, Streamlit (UI, custom CSS), Pandas (tables, CSV export), NumPy (statistics).

## 7. System Architecture
```
genetic-timetable-generator/
├── app.py                  Modern Streamlit UI (Setup / Timetable / Insights)
├── requirements.txt
├── README.md
├── ga/
│   ├── chromosome.py       gene, chromosome, population initialization
│   ├── fitness.py          penalty and fitness function
│   ├── selection.py        tournament selection
│   ├── crossover.py        class-wise crossover
│   ├── mutation.py         swap / room mutation (conflict-guided)
│   └── genetic_algorithm.py  main loop + elitism
├── data/sample_data.py     default sample input
├── utils/timetable.py      chromosome -> coloured HTML grids, tables, CSV
└── docs/                   presentation content and viva Q&A
```
`app.py` collects inputs, checks them (pre-flight check), calls `run_genetic_algorithm()`, then displays the best timetable (by class or by teacher) and graphs.

## 8. Genetic Algorithm Workflow
```
Random Population -> Fitness Evaluation -> Selection -> Crossover -> Mutation
        -> New Population (next generation) -> repeat -> Best Solution
```
(Elitism copies the best timetables unchanged into every new generation.)

## 9. Chromosome Representation
- **Gene** = one lecture: `{class, subject, teacher, day, period, room}`. Class, subject and teacher are fixed by the input; the GA decides `day`, `period` and `room`.
- **Chromosome** = list of all genes = one complete timetable.
- **Population** = a set of chromosomes (e.g. 100 timetables).

Gene number *i* is the same lecture in every chromosome, so crossover always gives valid timetables and every subject always gets its required number of lectures.

**No free period (guaranteed by design):** every class has exactly `days x periods` lectures. When the population is created, each class's slots are shuffled and handed out one per lecture (a random *permutation*), so no slot is empty and no two lectures of a class share a slot. Crossover and mutation only move whole class timetables or *swap* two lectures of the same class, so this property is never lost. The GA only has to remove teacher and room clashes.

If the subjects do not add up to the full week, the app can optionally fill the leftover periods with **activity periods** (Library, Sports, Self Study ...). These need no teacher and no room.

## 10. Fitness Function
```
Total Penalty = 10 x (Faculty + Class + Room + Unavailable + Invalid + Free) + 2 x Consecutive + 1 x Gaps
Fitness       = 1 / (1 + Total Penalty)
```
| Rule | Type | Weight |
|---|---|---|
| Teacher in two places at once | Hard | 10 |
| Class has two lectures at once | Hard | 10 |
| Room used twice at once | Hard | 10 |
| Teacher scheduled when unavailable | Hard | 10 |
| Invalid assignment (room too small / out of range) | Hard | 10 |
| **Free period** (a class slot with no lecture) | Hard | 10 |
| Same subject in consecutive periods | Soft | 2 |
| Empty period between lectures | Soft | 1 |

**Why 1 / (1 + P)?** Penalty 0 gives fitness 1 (perfect). Larger penalty gives a smaller fitness (always between 0 and 1). The "+1" avoids division by zero. Higher fitness is always better, which is what selection needs.

## 11. Selection
**Tournament selection (size 3):** pick 3 random timetables, the fittest becomes a parent. Good timetables win more often, but weak ones still have a chance, which keeps variety.

## 12. Crossover
**Class-wise crossover** (rate 0.8): for every class, flip a coin. Child 1 takes that class's whole timetable from parent 1 or parent 2, and child 2 takes it from the other parent. A class's timetable is a perfect arrangement of its slots, so copying it as one block keeps "no free period" true. (A plain single-point cut could split a class and leave empty slots.) With probability 0.2 the children are plain copies.

## 13. Mutation
Each gene is changed with probability = mutation rate (0.02). A mutated gene either **swaps its slot with another lecture of the same class** (70%, so no slot ever becomes empty) or **moves to another room** (30%). This adds new variety that crossover alone cannot create.

**Conflict-guided mutation:** a lecture that is clashing (teacher/room clash, teacher unavailable, room too small) is mutated much more often (30%), and its swap partner is chosen so that both teachers are free in each other's slots when possible. Lectures of the same subject in back-to-back periods get a smaller boost (15%). Random changes are spent where they are needed.

## 14. Elitism
The best 2 timetables of each generation are copied unchanged into the next generation. The best fitness therefore never decreases.

## 15. Implementation
- `create_population()` – random timetables (generation 0)
- `calculate_fitness()` – counts violations, applies penalties
- `tournament_selection()`, `class_crossover()`, `mutate()`
- `run_genetic_algorithm()` – loops over generations, applies elitism, stops early if penalty = 0, returns the best timetable and the history for the graph.

One **generation** = evaluate fitness, keep the elites, create children by selection + crossover + mutation, replace the old population.

## 16. How to Run (Windows + VS Code)
```
cd genetic-timetable-generator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```
The browser opens at http://localhost:8501. Click **Generate Timetable**.

## 17. Expected Output
- Pre-flight check showing lectures vs slots ("Perfect fit - no free period")
- Colour-coded timetable per class and per teacher (Subject, Teacher, Room) with every period filled, plus CSV download
- Initial fitness (about 0.002) and final fitness (up to 1.0)
- Generation vs Fitness graph rising, penalty graph falling
- Penalty breakdown table (free periods = 0), conflicts count, satisfied constraints (e.g. 540 / 540), before-vs-after view

## 18. Advantages
Fully automatic, handles many constraints, easy to add new rules, no brute force, visually explainable, real GA implemented from scratch.

## 19. Limitations
Randomized, so results differ per run; does not guarantee a perfect timetable; every class studies all listed subjects; lectures per class must equal days x periods (or be topped up with activity periods); no lab/multi-period lectures; slower for very large inputs.

## 20. Future Scope
Lab sessions (2 continuous periods), teacher workload limits, preferred time slots, export to Excel/PDF, saving inputs, multi-department support.

## 21. Conclusion
The project shows that a Genetic Algorithm can solve a real constraint-satisfaction problem. Starting from random timetables, selection, crossover, mutation and elitism steadily reduce the penalty until a valid timetable is found.

---

# Academic Explanation (student-friendly)

**What is a Genetic Algorithm?** A search method inspired by evolution: keep a population of candidate solutions, let the fittest "reproduce", add small random changes, and repeat. Over generations the solutions get better.

| Term | In this project |
|---|---|
| Chromosome | A complete timetable for all classes |
| Gene | One lecture with its day, period and room |
| Population | e.g. 100 different timetables |
| Fitness function | `1 / (1 + total penalty)` – how good a timetable is |
| Selection | Tournament of 3: the fittest becomes a parent |
| Crossover | Each class's timetable comes from parent 1 or parent 2 |
| Mutation | Swap two lectures of a class, or change a lecture's room |
| Elitism | Best 2 timetables are carried over unchanged |
| Generation | One full cycle of evaluate, select, crossover, mutate, replace |

## Mathematical Formulation
Let a timetable be *T* and violation counts be F (faculty), C (class), R (room), U (unavailable), I (invalid), E (free periods), S (consecutive), G (gaps).

```
P(T) = 10(F + C + R + U + I + E) + 2S + 1G
Fitness(T) = 1 / (1 + P(T))        0 < Fitness <= 1
```
The GA tries to **minimize P(T)**, which is the same as **maximizing Fitness(T)**. Hard rules have a large weight so the GA first removes real conflicts, then tidies soft problems.
