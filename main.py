from network import Network
from parameters import configs
from solve_problem import solve
from plot import plot_convergence, plot_scatter_legend

import random
import numpy as np
import sys

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

def paint_graph(ntw):
    try:
        while True:
            ntw.displayGraph()
    except KeyboardInterrupt:
        pass

# MAIN
# ==============================================================================

if __name__ == "__main__":

    random.seed(configs.seed)

    if configs.command == 'generate':
        ntw = Network(configs)

        if configs.print:
            print_info(ntw)

        if configs.paint:
            paint_graph(ntw)

        if configs.output:
            import pickle
            pickle.dump(ntw, configs.output)
            configs.output.close()

    elif configs.command == 'solve':
        import pickle
        ntw = pickle.load(configs.input)

        solution = solve(ntw, configs)
        if solution is None:
            if configs.output:
                configs.output.close()
            sys.exit(1)

        if configs.print:
            print(solution)

        if configs.output:
            configs.output.write(solution)
            configs.output.close()
    
    elif configs.command == 'plot':
        if configs.comparison:
            plot_scatter_legend(configs)
        if configs.history:
            plot_convergence(configs)

