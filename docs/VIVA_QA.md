# Viva Questions and Answers

1. **What is a Genetic Algorithm?** A search/optimization technique inspired by natural evolution that improves a population of solutions using selection, crossover and mutation.
2. **Why did you choose GA?** Timetabling has a huge search space and many constraints; GA finds good solutions without trying everything.
3. **What is a chromosome?** One complete timetable (a list of all lecture placements).
4. **What is a gene?** One lecture with its day, period and room (plus its fixed class, subject and teacher).
5. **What is a population?** A group of many timetables (100 by default) that evolve together.
6. **What is a fitness function?** A formula that scores a timetable: Fitness = 1 / (1 + Total Penalty).
7. **What is selection?** Choosing better timetables as parents. We use tournament selection of size 3.
8. **What is crossover?** Combining two parents to make two children. Here each class's whole timetable is taken from one parent or the other (class-wise crossover), so no free period is created.
9. **What is mutation?** A small random change: swapping two lectures of a class, or moving a lecture to another room. Clashing lectures are mutated more often (guided mutation).
10. **What is elitism?** Copying the best timetables unchanged into the next generation so they are never lost.
11. **What is a generation?** One full cycle: evaluate, select, crossover, mutate, replace population.
12. **Why is mutation necessary?** It adds new variety and stops the population getting stuck with similar solutions.
13. **What if the mutation rate is too high?** The search becomes random and good solutions get destroyed.
14. **What if the mutation rate is too low?** Little variety, so the GA may get stuck in a poor solution.
15. **How does the timetable avoid conflicts?** It does not avoid them directly. Conflicts get high penalties, so timetables with fewer clashes survive and reproduce.
16. **Why is GA suitable for timetable generation?** Many constraints, huge search space, and a near-optimal solution is acceptable.
17. **What are the limitations?** Results are random per run, no guarantee of a perfect timetable, needs tuning, slower for big inputs.
18. **How is it different from brute force?** Brute force tries every timetable (impossible here); GA improves good solutions step by step.
19. **What if no perfect timetable exists?** The GA returns the best one found, with the lowest penalty and the remaining conflicts listed.
20. **How could this project be improved?** Add lab sessions, teacher workload limits, preferred slots and Excel/PDF export.
21. **How do you make sure there is no free period?** Every class gets exactly days x periods lectures and each class's slots are a permutation. Crossover copies whole class timetables and mutation only swaps lectures inside a class, so every slot stays filled. A hard "free period" rule in the fitness function double-checks it.
22. **What if a class has fewer lectures than slots?** The pre-flight check tells you how many to add, or you can switch on activity periods (Library, Sports ...) to fill the leftover slots.
