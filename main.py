from network import Network
from parameters import configs
from solve_problem import solve
from plot import plot_convergence, plot_scatter_legend

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
            pass

        if configs.paint:
            paint_graph(ntw, configs.paint_seed)

        if configs.output:
            import pickle
            pickle.dump(ntw, configs.output)
            configs.output.close()

    elif configs.command == 'modify':
        pass

    elif configs.command == 'analyze':
        # Analyze the network with or without a given solution
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
        pass
    
    elif configs.command == 'plot':
        # Plot files
        if configs.comparison:
            plot_scatter_legend(configs)
        if configs.history:
            plot_convergence(configs)



