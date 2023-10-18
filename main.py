from network import Network
from parameters import configs
from solve_problem import solve
from plot import plot_convergence, plot_scatter_legend
from arrange import get_pareto_front_from_files
from analyze import get_table

import random
import numpy as np
import sys

def paint_graph(ntw, seed=1):
    try:
        while True:
            print("Showing graph painted with seed = {}".format(seed))
            ntw.displayGraph(seed)
            seed += 1
    except KeyboardInterrupt:
        pass

# MAIN
# ==============================================================================

if __name__ == "__main__":

    random.seed(configs.seed)

    if configs.command == 'generate':
        # Generate the network
        ntw = Network(configs)

        if configs.print:
            print(ntw.getTotalNodeMemory())
            print(ntw.getTotalTaskMemory())
            print(ntw.memory)
            print(ntw.getMinimumNNodesNeeded())

        if configs.paint:
            paint_graph(ntw, configs.paint_seed)

        if configs.output:
            import pickle
            pickle.dump(ntw, configs.output)
            configs.output.close()

        if not ntw.checkMemoryRequirements():
            print('WARNING: Memory requirements could not be satisfied.')
            print('- Total node memory: {}'.format(
                    ntw.getTotalNodeMemory()))
            print('- Total task memory: {}'.format(
                    ntw.getTotalTaskMemory()))
            print('Change memory limit or amount of tasks and try again')
            sys.exit(1)

    elif configs.command == 'modify':
        import pickle
        ntw = pickle.load(configs.input)

    elif configs.command == 'solve':
        # Solve a problem using a network and an optimization algorithm
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

    elif configs.command == 'arrange':
        # Arrange files of solutions and prepare them for ploting
        array = get_pareto_front_from_files(configs)

        s = ''
        for x, y in array:
            s += '{} {}\n'.format(x,y)
        s = s[:-1]

        if configs.print:
            print(s)

        if configs.output:
            configs.output.write(s)
            configs.output.close()
             
    elif configs.command == 'analyze':
        # Analyze the solutions
        table = get_table(configs)

        if configs.print:
            print(table)

        if configs.output:
            configs.output.write(table)
            configs.output.close()
    
    elif configs.command == 'plot':
        # Plot files
        if configs.comparison:
            plot_scatter_legend(configs)
        if configs.history:
            plot_convergence(configs)



