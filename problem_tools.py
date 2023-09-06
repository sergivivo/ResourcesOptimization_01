from pymoo.core.sampling  import Sampling
from pymoo.core.crossover import Crossover
from pymoo.core.mutation  import Mutation
from pymoo.core.duplicate import ElementwiseDuplicateElimination
from pymoo.core.repair    import Repair
from pymoo.core.callback  import Callback

import numpy as np
import random
import datetime

"""
Service instantiated on a single node
"""
class MySampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, 1),  None, dtype=object)
        for i in range(n_samples):
            matrix = np.zeros((problem.N_TASKS, problem.N_NODES), np.uint8)
            for row in range(problem.N_TASKS):
                col = random.randrange(problem.N_NODES)
                matrix[row, col] = 1

            X[i,0] = matrix

        return X

class MyCrossover(Crossover):
    def __init__(self):
        super().__init__(n_parents = 2, n_offsprings = 2)

    def _do(self, problem, X, **kwargs):
        n_parents, n_matings, n_var = X.shape[:3]
        Y = np.full_like(X, None, dtype=object)

        for k in range(n_matings):
            p1, p2 = X[0, k, 0], X[1, k, 0]
            off1, off2 = [], []

            for i in range(problem.N_TASKS):
                if random.random() < 0.5:
                    off1.append(p1[i])
                    off2.append(p2[i])
                else:
                    off1.append(p2[i])
                    off2.append(p1[i])

            Y[0, k, 0], Y[1, k, 0] = np.array(off1, np.uint8), np.array(off2, np.uint8)

        return Y

class MyRepair(Repair):

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            for row in range(problem.N_TASKS):
                available = problem.network.getNodeAvailableMemoryArray(X[i,0])
                task_memory = problem.network.getTask(row).memory
                curr_idx = np.nonzero(X[i, 0][row])[0]

                # Check if task surpasses available memory
                if task_memory > available[curr_idx]:

                    # We search for a new node
                    indexes = np.arange(len(available), dtype=np.uint16)

                    # Filter so that we only choose between nodes with enough
                    # available memory to hold this task
                    filtered = indexes[available > task_memory]

                    # Subtract both sets and choose a new column
                    choices = np.setdiff1d(filtered, curr_idx)

                    if choices.size > 0:
                        # Set to zero current column
                        X[i, 0][row, curr_idx] = 0

                        # Set to one new columns
                        col = random.choice(choices)
                        X[i, 0][row, col] = 1

        return X

class MyMutation(Mutation):
    """Change the position of the 1 in a row with a given probability"""
    def __init__(self, p=0.05):
        super().__init__()
        self.probability = p

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            for row in range(problem.N_TASKS):
                if random.random() < self.probability:
                    available = problem.network.getNodeAvailableMemoryArray(X[i,0])
                    indexes = np.arange(len(available), dtype=np.uint16)

                    # Filter so that we only choose between nodes with enough
                    # available memory to hold this task
                    task_memory = problem.network.getTask(row).memory
                    filtered = indexes[available > task_memory]

                    # Subtract both sets and choose a new column
                    curr_idxs = np.nonzero(X[i, 0][row])
                    choices = np.setdiff1d(filtered, curr_idxs)

                    if choices.size > 0:
                        # Set to zero current column
                        for col in curr_idxs:
                            X[i, 0][row, col] = 0

                        # Set to one new columns
                        col = random.choice(choices)
                        X[i, 0][row, col] = 1

        return X

class MyDuplicateElimination(ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return np.array_equal(a.X[0], b.X[0])

class MyCallback(Callback):
    def __init__(self, save_history=False):
        super().__init__()
        self.save_history = save_history
        if save_history:
            self.string_history = ""
        else:
            self.string_solution = ""

    def notify(self, algorithm):
        f = algorithm.pop.get('F_original')

        # Save current solution or append to history
        curr_sol = algorithm.opt.get('F_original')

        if self.save_history:
            dt_now = datetime.datetime.now()
        else:
            self.string_solution = ""

        for o1, o2 in curr_sol:
            if self.save_history:
                self.string_history += "{} {} {} {}\n".format(
                        dt_now, algorithm.n_gen, o1, o2)
            else:
                self.string_solution += "{} {}\n".format(o1, o2)




