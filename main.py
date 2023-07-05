from network import Network
from config import *

import random

# MAIN
# ==============================================================================

if __name__ == "__main__":
    random.seed(SEED)

    ntw = Network()

    print("User tasks:")
    for u in range(N_USERS):
        print(f"\tUser {u}:", ntw.getUserTasks(u))
    print()

    print("User/Node distance matrix:")
    print(ntw.getUserNodeDistanceMatrix())
    print()

    # Randomly assign tasks to nodes without checking limits
    for i in range(N_TASKS):
        ntw.assignTask(i, random.randrange(N_NODES))

    print("Executing tasks on each node:")
    for n in range(N_NODES):
        print(f"\tNode {n}:", ntw.getNodeExecutingTasks(n))
    print()

    print("Task/Node assignment matrix:")
    print(ntw.getTaskNodeAssignmentMatrix())
    print()

    print("Task memory list:")
    print(ntw.getTaskMemoryArray())
    print()

    print("Node memory list:")
    print(ntw.getNodeMemoryArray())
    print()

    print("Task memory assigned to each node matrix:")
    print(ntw.getTaskNodeMemoryMatrix())
    print()

#    try:
#        while True:
#            ntw.displayGraph()
#    except KeyboardInterrupt:
#        pass

