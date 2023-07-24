from network import Network
from parameters import configs

import random
import numpy as np

from problems import Problem01v3
from problems import MySampling
from problems import MyCrossover
from problems import MyMutation
from problems import MyDuplicateElimination

from pymoo.algorithms.moo.nsga2 import NSGA2

from pymoo.termination import get_termination

from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling

from pymoo.optimize import minimize

def print_info(ntw):

    print("User tasks:")
    for u in range(configs.n_users):
        print(f"\tUser {u}:", ntw.getUserTasks(u))
    print()

    print("Task/User assignment matrix:")
    print(ntw.getTaskUserAssignmentMatrix())
    print()

    print("User/Node distance matrix:")
    print(ntw.getUserNodeDistanceMatrix())
    print()

    # Randomly assign tasks to nodes without checking limits
    for i in range(configs.n_tasks):
        ntw.assignTask(i, random.randrange(configs.n_nodes))

    print("Executing tasks on each node:")
    for n in range(configs.n_nodes):
        print(f"\tNode {n}:", ntw.getNodeExecutingTasks(n))
    print()

    tnam = ntw.getTaskNodeAssignmentMatrix()
    print("Task/Node assignment matrix:")
    print(tnam)
    print()

    npt = np.sum(tnam, axis=1)
    print("Nodes per task list:")
    print(npt)
    print()

    print("Less than 2 nodes?")
    print(np.all(npt < 2))
    print()

    tpn = np.sum(tnam, axis=0)
    print("Tasks per node list:")
    print(tpn)
    print()

    tma = ntw.getTaskMemoryArray()
    print("Task memory list:")
    print(tma)
    print()

    nma = ntw.getNodeMemoryArray()
    print("Node memory list:")
    print(nma)
    print()

    tnmm = ntw.getTaskNodeMemoryMatrix()
    print("Task memory assigned to each node matrix:")
    print(tnmm)
    print()

    tmpn = np.sum(tnmm, axis=0)
    print("Total task memory assigned to each node:")
    print(tmpn)
    print()

    print("Remaining memory on each node:")
    print(nma - tmpn)
    print()

    print("Enough memory?")
    print(nma > tmpn)
    print(np.all(nma > tmpn))
    print()

def paint_graph():
    try:
        while True:
            ntw.displayGraph()
    except KeyboardInterrupt:
        pass

# MAIN
# ==============================================================================

if __name__ == "__main__":
    random.seed(configs.seed)

    ntw = Network(configs)

    problem = Problem01v3(ntw)

    algorithm = RNSGA2(pop_size = configs.pop_size,
        sampling=MySampling(),
        crossover=MyCrossover(),
        mutation=MyMutation(),
        eliminate_duplicates=MyDuplicateElimination()
    )

    """
    algorithm = NSGA2(
        sampling=IntegerRandomSampling(),
        crossover=SBX(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
        mutation=PM(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
        eliminate_duplicates=True
    )
    """

    termination = get_termination(configs.termination_type, configs.n_gen)

    res = minimize(
        problem,
        algorithm,
        termination=termination,
        seed=configs.seed,
        verbose=True
    )

    for i in range(len(res.X)):
        print(res.X[i][0])
        print(res.F[i])
        print()

    

