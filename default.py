
# Random
SEED = 727

# Network generation
P = 0.10
MIN_WEIGHT = 5.
MAX_WEIGHT = 20.

N_NODES = 10
NODE_MEMORY_CHOICE = list(range(256, 2049, 128))
NODE_MAX_TASKS_CHOICE = list(range(100,101))

N_TASKS = 20
TASK_MIN_MEMORY = 30
TASK_MAX_MEMORY = 800

N_USERS = 3

OUTPUT_FILE = 'graph01.gefx'

# Pymoo optimization problem solving
POP_SIZE = 100
ALGORITHM = 'NSGA2'
N_GEN = 100
TERMINATION_TYPE = 'n_gen'

MUTATION_PROB = 0.1



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

