import pulp

import numpy as np
import random

class ProblemILP():

    def __init__(self, network, l=0.0):
        self.network = network

        # Define the constants
        self.N_TASKS = network.getNTasks()
        self.N_USERS = network.getNUsers()
        self.N_NODES = network.getNNodes()

        self.TASK_MEM_ARRAY = network.getTaskMemoryArray()
        self.NODE_MEM_ARRAY = network.getNodeMemoryArray()

        self.l = l # lambda for converting bimode to singlemode

        # Values needed for normalization
        self.f1_min = 0.
        self.f1_max = np.max(network.getUserNodeDistanceMatrix())
        self.f2_min = 0.
        self.f2_max = self.N_NODES

        # Defining the problem
        self.prob = pulp.LpProblem('Node selection problem', pulp.LpMinimize)

        # Defining the variables
        self.tnam = pulp.LpVariable.dicts(
                "TaskNodeAssignmentMatrix",
                (range(self.N_TASKS), range(self.N_NODES)),
                cat="Binary")

        self.n_sel = pulp.LpVariable.dicts(
                "SelectedNodeVector",
                range(self.N_NODES),
                cat="Binary") # node selection for task assignment


        # Objective function
        self._setObjectiveFunction()

        # Constraints
        for t in range(self.N_TASKS):
            self.prob += pulp.lpSum(self.tnam[t]) == 1
            # Ensure each service is assigned to a single node

        for t in range(self.N_TASKS):
            for n in range(self.N_NODES):
                self.prob += self.tnam[t][n] <= self.n_sel[n]
                # Ensure that a service is assigned to a selected node

        for n in range(self.N_NODES):
            self.prob += pulp.lpSum(
                    [self.TASK_MEM_ARRAY[t] * self.tnam[t][n]
                        for t in range(self.N_TASKS)]
                ) <= self.NODE_MEM_ARRAY[n]
            # Ensure that node's memory limit is not surpassed

    def _setObjectiveFunction(self):
        self.prob += pulp.lpSum(self.n_sel), "Number of nodes with at least one task"

    def _normalize(self, f1, f2):
        f1_norm = (f1 - self.f1_min) / (self.f1_max - self.f1_min)
        f2_norm = (f2 - self.f2_min) / (self.f2_max - self.f2_min)
        return f1_norm, f2_norm

    def solve(self):
        self.prob.solve()
        return pulp.LpStatus[self.prob.status]
    
    def getSolutionString(self):
        """Get solution for printing, only after call to method solve"""
        s = ""
        for t in range(self.N_TASKS):
            for n in range(self.N_NODES):
                s += "{: <2}".format(int(pulp.value(self.tnam[t][n])))
            s += '\n'
        return s

    def getSingleModeObjective(self):
        return pulp.value(self.prob.objective)

    def getMultiModeObjective(self, i):
        pass

    def changeLambda(self, l):
        self.l = l
        # TODO: change objective according to this new lambda

if __name__ == '__main__':
    from parameters import configs
    from network import Network
    import pickle

    random.seed(configs.seed)
    ntw = pickle.load(configs.input)

    problem = ProblemILP(ntw)

    problem.solve()
    print(problem.getSolutionString())

