import numpy as np

# Random
SEED = 727

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

OUTPUT_FILE = 'graph01.gefx'

# Pymoo optimization problem solving
POP_SIZE = 100
ALGORITHM = 'NSGA2'
N_GEN = 100
TERMINATION_TYPE = 'n_gen'

MUTATION_PROB = 0.2

N_PARTITIONS = 16
REF_POINTS = '[[18., 6.], [15., 8.], [21., 5.]]'

LAMBDA = 0.5 # used for converting bimode to single-mode


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

