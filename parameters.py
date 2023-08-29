import argparse
import sys
import ast
from default import *

class Range(object):
    """Used for ranges of values that are not integers"""
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__ (self, other):
        return self.start <= other <= self.end
    def __repr__(self):
        return "[{}, {}]".format(self.start, self.end)

def type_point_list(arg):
    return ast.literal_eval('%s' % arg)

parser = argparse.ArgumentParser(description="Arguments")
subparsers = parser.add_subparsers(dest='command')

# Random
parser.add_argument('--seed', type=int, default=SEED, help='Seed used for random generation')

# Network generation
parser_generate = subparsers.add_parser('generate', help='Generate the network')

parser_generate.add_argument('-p', '--probability', type=float, choices=[Range(0.0, 1.0)], default=P, help='Probability of a node being connected to another node. Mind that there\'s at least one edge on each node to enforce the graph being connected, so this value will be meaningful if the probability is greater than 1/NODES. Conflicts with --edges.')
parser_generate.add_argument('-e', '--edges', type=int, default=E, help='Number of edges to attach from a new node to existing nodes. Conflicts with --probability.')
parser_generate.add_argument('--min_weight', type=float, default=MIN_WEIGHT, help='Minimum weight that an edge can have')
parser_generate.add_argument('--max_weight', type=float, default=MAX_WEIGHT, help='Maximum weight that an edge can have')

parser_generate.add_argument('--n_nodes', type=int, default=N_NODES, help='Number of server nodes in the network')

parser_generate.add_argument('--n_tasks', type=int, default=N_TASKS, help='Number of tasks to be executed in the network')
parser_generate.add_argument('--task_min_memory', type=float, default=TASK_MIN_MEMORY, help='Minimum memory that a task requires to execute')
parser_generate.add_argument('--task_max_memory', type=float, default=TASK_MAX_MEMORY, help='Maximum memory that a task requires to execute')

parser_generate.add_argument('--n_users', type=int, default=N_USERS, help='Number of users in the network')

parser_generate.add_argument('--paint', action='store_true', help='Paint the graph with Matplotlib')
parser_generate.add_argument('--print', action='store_true', help='Print on console useful information about the generated network')
parser_generate.add_argument('-o', '--output', type=argparse.FileType('wb'), help='Output file path used for storing the network data')

# Pymoo optimization problem solving
parser_solve = subparsers.add_parser('solve', help='Solve optimization problem')

parser_solve.add_argument('-i', '--input', type=argparse.FileType('rb'), help='Input file path used for generating the network')

parser_solve.add_argument('--pop_size', type=int, default=POP_SIZE, help='Population size')
parser_solve.add_argument('--algorithm', type=str, choices=ALGORITHMS, default=ALGORITHM, help='Name of the algorithm to be used to solve the problem')

parser_solve.add_argument('--termination_type', type=str, default=TERMINATION_TYPE, help='Termination type for the algorithm')
parser_solve.add_argument('--n_gen', type=int, default=N_GEN, help='Number of generations as termination parameter')

parser_solve.add_argument('--mutation_prob', type=float, choices=[Range(0.0, 1.0)], default=MUTATION_PROB, help='Probability of mutation in task assignment to nodes')

parser_solve.add_argument('-v', '--verbose', action='store_true')
parser_solve.add_argument('--print', action='store_true', help='Print on console useful information about the generated network')

parser_solve.add_argument('-o', '--output', type=argparse.FileType('w'), help='Output file path used for storing the solution data')
parser_solve.add_argument('--save_history', action='store_true', help='Will save history to retrieve the evolution of the solutions')

# Specific parameter for algorithms that need reference directions
parser_solve.add_argument('--n_partitions', type=int, default=N_PARTITIONS, help='Specific parameter for algorithm NSGA3. Set the number of partitions for reference directions.')

# Specific parameter for algorithms that need reference point
parser_solve.add_argument('--ref_points', type=type_point_list, default=REF_POINTS, help='Specific parameter for algorithms that requiere reference points')

# Solution ploting
parser_plot = subparsers.add_parser('plot', help='Plot the resulting data from the solution')

parser_plot.add_argument('-i', '--input', nargs='+', type=argparse.FileType('r'), help='List of input file paths used for plotting the solutions')

parser_plot.add_argument('--history', action='store_true', help='Plot a single solution including the history representing the evolution with the form of a scatter plot')

parser_plot.add_argument('--comparison', action='store_true', help='Plot multiple solutions comparing them in the same graph with the form of a scatter plot')
parser_plot.add_argument('--legend', nargs='*', type=str, help='List of names for the different inputs to be plotted and added to the legend')

parser_plot.add_argument('--title', type=str, default='', help='Title of the plot')
parser_plot.add_argument('--x_label', type=str, default='', help='Label for X axis')
parser_plot.add_argument('--y_label', type=str, default='', help='Label for Y axis')

parser_plot.add_argument('-o', '--output', type=argparse.FileType('wb'), help='Output file path used for saving plot result')


# CONFIG GENERATOR
# ==============================================================================
configs = parser.parse_args()
configs.node_memory_choice = NODE_MEMORY_CHOICE
configs.node_max_tasks_choice = NODE_MAX_TASKS_CHOICE



if __name__ == '__main__':
    print(configs)


