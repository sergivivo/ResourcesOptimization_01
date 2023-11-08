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
    def __init__(self, n_replicas=1):
        super().__init__()
        self.n_replicas = n_replicas

    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, 1),  None, dtype=object)
        for i in range(n_samples):
            matrix = np.zeros((problem.N_TASKS, problem.N_NODES), np.uint8)
            for row in range(problem.N_TASKS):
                col_list = random.sample(
                        range(problem.N_NODES),
                        random.randint(1, self.n_replicas)
                    )
                for col in col_list:
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
    def __init__(self, n_replicas=1):
        super().__init__()
        self.n_replicas = n_replicas

    def _do(self, problem, X, **kwargs):
        task_memory = problem.network.getTaskMemoryArray()
        for i in range(len(X)):
            for tid in np.lexsort((task_memory,))[::-1]:

                tmem = task_memory[tid]
                available = problem.network.getNodeAvailableMemoryArray(X[i,0])

                node_idxs_1 = np.flatnonzero(X[i, 0][tid])
                node_idxs_0 = np.setdiff1d(np.arange(problem.N_NODES), node_idxs_1)

                # From all ones, select those who surpass the available memory
                node_idxs_1_filter = node_idxs_1[available[node_idxs_1] < 0.]
                len1 = len(node_idxs_1_filter)

                # From all zeros, select those who have enough available memory
                # to hold this specific task
                node_idxs_0_filter = node_idxs_0[available[node_idxs_0] - tmem > 0.]
                len0 = len(node_idxs_0_filter)

                if len0 != 0 :
                    if len0 < len1:
                        # Remove overflowing replicas
                        for nid in node_idxs_1_filter[len0:]:
                            X[i,0][tid,nid] = 0

                        node_idxs_1_filter = node_idxs_1_filter[:len0]
                        len1 = len0

                    # Move to make nodes more compact
                    n0_sorted = node_idxs_0_filter[
                            np.lexsort((available[node_idxs_0_filter],))
                        ]

                    for j in range(len1):
                        orig = node_idxs_1_filter[j]
                        dest = n0_sorted[j]
                        X[i,0][tid,orig] = 0
                        X[i,0][tid,dest] = 1

        return X

class MyMutation(Mutation):
    def __init__(self, p_move=0.1, p_change=0.1, n_replicas=1):
        super().__init__()
        self.p_move   = p_move   # Change position of 1
        self.p_change = p_change # Change 1 to 0 or 0 to 1
        self.n_replicas = n_replicas

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            rnd = random.random()

            if rnd < self.p_move:
                # First type: move assigned task to a different node
                row = random.randrange(problem.N_TASKS)

                nid_array_1 = np.flatnonzero(X[i,0][row])
                nid_array_0 = np.setdiff1d(
                        np.arange(problem.N_NODES),
                        nid_array_1
                    )

                # Ensure that selected node can hold that task
                tmem = problem.network.getTaskMemoryArray()[row]
                available = problem.network.getNodeAvailableMemoryArray(X[i,0])
                nid_array_0_filter = nid_array_0[available[nid_array_0] >= tmem]

                if nid_array_0_filter.size > 0:
                    col_src  = np.random.choice(nid_array_1)
                    col_dest = np.random.choice(nid_array_0_filter)
                    X[i,0][row, col_src ] = 0
                    X[i,0][row, col_dest] = 1

            elif self.n_replicas > 1 and rnd < self.p_move + self.p_change:
                # Second type: change task assignment state within a node
                row = random.randrange(problem.N_TASKS)
                nid_array_1 = np.flatnonzero(X[i,0][row])

                # Update rnd to fit between 0 and 1
                rnd = (rnd - self.p_move) / self.p_change

                if nid_array_1.size >= self.n_replicas:
                    # Change 1 to 0 with 100% probability
                    ch_01 = False
                elif nid_array_1.size <= 1:
                    # Change 0 to 1 with 100% probability
                    ch_01 = True
                elif rnd < 0.5:
                    # Change 1 to 0 with 50% probability
                    ch_01 = False
                else:
                    # Change 0 to 1 with 50% probability
                    ch_01 = True

                if ch_01:
                    nid_array_0 = np.setdiff1d(
                            np.arange(problem.N_NODES),
                            nid_array_1
                        )

                    # Ensure that selected node can hold that task
                    tmem = problem.network.getTaskMemoryArray()[row]
                    available = problem.network.getNodeAvailableMemoryArray(X[i,0])
                    nid_array_0_filter = nid_array_0[available[nid_array_0] >= tmem]

                    if nid_array_0_filter.size > 0:
                        col = np.random.choice(nid_array_0)
                        X[i,0][row,col] = 1
                    
                else:
                    col = np.random.choice(nid_array_1)
                    X[i,0][row,col] = 0

        return X

class MyMutation_backup(Mutation):
    """Change the position of the 1 in a row with a given probability"""
    def __init__(self, p=0.05):
        super().__init__()
        self.probability = p

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            if random.random() < self.probability:
                row = random.randrange(problem.N_TASKS)
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

        for o in curr_sol:
            if self.save_history:
                self.string_history += "{} {} ".format(
                        dt_now, algorithm.n_gen)

                for o_n in o:
                    self.string_history += "{} ".format(o_n)

                self.string_history += '\n'

            else:
                for o_n in o:
                    self.string_solution += "{} ".format(o_n)

                self.string_solution += '\n'


if __name__ == '__main__':
    from parameters import configs
    from network import Network
    from problems import Problem01v3
    import pickle

    random.seed(1)
    np.random.seed(1)

    ntw = pickle.load(configs.input)

    problem = Problem01v3(ntw)
    X = MySampling(n_replicas=1)._do(problem, n_samples=1)
    X_r = MyRepair(n_replicas=1)._do(problem, X)[0,0].copy()
    while True:
        X_m = MyMutation(p_move=0.5, p_change=0.5, n_replicas=1)._do(problem, X)[0,0].copy()

        print(X_r)
        print()
        print(X_m)
        print()
        print(X_r - X_m)
        print('-----')

        X_r = X_m
        input()

