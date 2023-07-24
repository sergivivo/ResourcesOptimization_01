import argparse

# DEFAULT
# ==============================================================================
# Random
SEED = 727

# Network generation
P = 0.1
MIN_WEIGHT = 1.
MAX_WEIGHT = 20.

N_NODES = 10
NODE_MEMORY_CHOICE = [128, 256, 512, 1024, 2048, 4096]
NODE_MAX_TASKS_CHOICE = list(range(100,101))

N_TASKS = 20
TASK_MIN_MEMORY = 10
TASK_MAX_MEMORY = 200

N_USERS = 3

OUTPUT_FILE = 'graph01.gefx'

# Pymoo optimization problem solving
POP_SIZE = 100
ALGORITHM = 'NSGA2'
N_GEN = 100
TERMINATION_TYPE = 'n_gen'

MUTATION_PROB = 0.05


# ARGUMENT PARSE
# ==============================================================================
class Range(object):
    """Used for ranges of values that are not integers"""
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__ (self, other):
        return self.start <= other <= self.end
    def __repr__(self):
        return "[{}, {}]".format(self.start, self.end)

ALGORITHMS = [
        'NSGA2',
        'RNSGA2',
        'NSGA3',
        'UNSGA3',
        'RNSGA3',
        'MOEAD',
        'AGEMOEA',
        'CTAEA',
        'SMSEMOA',
        'RVEA']

parser = argparse.ArgumentParser(description="Arguments")

# Random
parser.add_argument('--seed', type=int, default=SEED, help='Seed used for random generation')

# Network generation
parser.add_argument('-p', type=float, choices=[Range(0.0, 1.0)], default=P, help='Probability of a node being connected to another node. Mind that there\'s at least one edge on each node to enforce the graph being connected, so this value will be meaningful if the probability is greater than 1/NODES.')
parser.add_argument('--min_weight', type=float, default=MIN_WEIGHT, help='Minimum weight that an edge can have')
parser.add_argument('--max_weight', type=float, default=MAX_WEIGHT, help='Maximum weight that an edge can have')

parser.add_argument('--n_nodes', type=int, default=N_NODES, help='Number of server nodes in the network')

parser.add_argument('--n_tasks', type=int, default=N_TASKS, help='Number of tasks to be executed in the network')
parser.add_argument('--task_min_memory', type=float, default=TASK_MIN_MEMORY, help='Minimum memory that a task requires to execute')
parser.add_argument('--task_max_memory', type=float, default=TASK_MAX_MEMORY, help='Maximum memory that a task requires to execute')

parser.add_argument('--n_users', type=int, default=N_USERS, help='Number of users in the network')

# Pymoo optimization problem solving
parser.add_argument('--pop_size', type=int, default=POP_SIZE, help='Population size')
parser.add_argument('--algorithm', type=str, choices=ALGORITHMS, default=ALGORITHM, help='Name of the algorithm to use for solving the problem')
parser.add_argument('--termination_type', type=str, default=TERMINATION_TYPE, help='Termination type for the algorithm')
parser.add_argument('--n_gen', type=int, default=N_GEN, help='Number of generations as termination parameter')

parser.add_argument('--mutation_prob', type=float, choices=[Range(0.0, 1.0)], default=MUTATION_PROB, help='Probability of mutation in task assignment to nodes')

# CONFIG GENERATOR
# ==============================================================================
configs = parser.parse_args()
configs.node_memory_choice = NODE_MEMORY_CHOICE
configs.node_max_tasks_choice = NODE_MAX_TASKS_CHOICE

if __name__ == '__main__':
    print(configs)
