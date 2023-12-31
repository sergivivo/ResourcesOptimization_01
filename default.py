import numpy as np

# Random
SEED = 722

# Network generation
E = 2
MIN_WEIGHT = 5.
MAX_WEIGHT = 20.

N_NODES = 10
NODE_MEMORY_CHOICE = [512, 1024, 2048, 4096]
NODE_MEMORY_PARETO_SHAPE = 1.16
NODE_MAX_TASKS_CHOICE = list(range(100,101))

N_TASKS = 20
TASK_MEMORY_PARETO_SHAPE = 0.8
TASK_MIN_MEMORY = 30
TASK_MAX_MEMORY = 1500

N_USERS = 3
P = 0.3

GROUP_SIZE = 5
POPULARITY = 0.5
SPREADNESS = 0.5

OUTPUT_FILE = 'graph01.gefx'

# Pymoo optimization problem solving
POP_SIZE = 100
ALGORITHM = 'NSGA2'
N_GEN = 100
TERMINATION_TYPE = 'n_gen'

N_REPLICAS = 1
MUTATION_PROB_MOVE     = 0.1
MUTATION_PROB_CHANGE   = 0.1
MUTATION_PROB_BINOMIAL = 0.1

N_PARTITIONS = 16
REF_POINTS = '[[18., 6.], [15., 8.], [21., 5.]]'

LAMBDA = 0.5 # used for converting bimode to single-mode

OBJ_LIST = ['distance', 'nodes', 'hops', 'occupation', 'variance']
OBJ_DESCRIPTION = [
        'Mean latency between users/services',
        'Occupied nodes',
        'Mean hops to service',
        'Mean node occupation ratio',
        'Node occupation ratio variance'
    ]

ALGORITHMS = [
        'NSGA2',
        'RNSGA2',
        'NSGA3',
        'UNSGA3',
        'RNSGA3',
        'AGEMOEA',
        'CTAEA',
        'SMSEMOA',
        'RVEA',
        'ILP']

SAMPLING_VERSION = 0
CROSSOVER_VERSION = 2
MUTATION_VERSION = 1



