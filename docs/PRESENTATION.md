# Presentation Content (10 slides)

## Slide 1 – Title
- AI-Based College Timetable Generator Using Genetic Algorithm
- Subject: AISC (Artificial Intelligence and Soft Computing)
- Name, Roll No., Class, Guide
**Say:** "My project automatically creates a college timetable using a Genetic Algorithm that I implemented myself."

## Slide 2 – Problem Statement
- Manual timetable making is slow and error-prone
- Teachers, rooms and classes must not clash
- Huge number of possible timetables
- Brute force is impossible
**Say:** "With 3 classes and 90 lectures, the number of arrangements is astronomically large, so we need a smart search method."

## Slide 3 – Objective
- Generate a clash-free timetable automatically
- Minimize faculty, class and room clashes
- No free period: every period of every class is filled
- Reduce repeated subjects
- Show GA improvement visually
**Say:** "The goal is a valid timetable with minimum penalty, and to show clearly how a GA improves it."

## Slide 4 – Introduction to Genetic Algorithm
- Inspired by natural evolution (survival of the fittest)
- Works on a population of solutions
- Uses selection, crossover and mutation
- Good for optimization problems
**Say:** "Like nature: good solutions reproduce, children mix their parents' traits, and random mutation adds variety."

## Slide 5 – GA Workflow
- Random population, then fitness evaluation
- Selection, crossover, mutation
- Elitism keeps the best solutions
- Repeat for many generations, return the best
**Say:** "Show the flow diagram: Population, Fitness, Selection, Crossover, Mutation, New Generation, repeat."

## Slide 6 – Chromosome and Fitness Function
- Gene = one lecture (class, subject, teacher, day, period, room)
- Chromosome = full timetable
- Total Penalty = weighted sum of conflicts
- Fitness = 1 / (1 + Total Penalty)
**Say:** "Hard conflicts cost 10 each, soft ones 1 or 2. Zero penalty means fitness 1, a perfect timetable."

## Slide 7 – Project Architecture
- app.py: Streamlit UI
- ga/: chromosome, fitness, selection, crossover, mutation, main loop
- data/: sample input, utils/: timetable table builder
- Python, Streamlit, Pandas, NumPy
**Say:** "The GA code is in separate small files, one per GA component, and none of it is hidden inside a library."

## Slide 8 – Working Demonstration
- Show default sample data and GA settings
- Click Generate Timetable
- Show the progress bar and the final coloured timetable
- Change a setting (e.g. mutation rate) and run again
**Say:** "Run the live demo. Point out Subject, Teacher and Room in each cell."

## Slide 9 – Results
- Initial fitness about 0.002, final fitness 1.0
- Hard conflicts reduced to 0, all constraints satisfied
- Generation vs Fitness graph rises, penalty graph falls
- Initial vs final timetable comparison
**Say:** "The graph proves the GA is really improving, from hundreds of penalty points down to zero."

## Slide 10 – Conclusion and Future Scope
- GA successfully generates valid timetables
- Simple, explainable and extendable
- Future: lab sessions, teacher workload, preferred slots, Excel/PDF export
- Thank you / Questions
**Say:** "A GA can solve real scheduling problems. Future versions can add more real-world constraints."
