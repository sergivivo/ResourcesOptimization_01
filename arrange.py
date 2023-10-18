import numpy as np
import random
from file_utils import parse_file

def get_pareto_front_from_array(array):
    idx_sorted = np.lexsort((array[:,1], array[:,0]))
    # Investigar si para una misma X ordena también la Y de menor a mayor
    array_sorted = array[idx_sorted]

    min_y = 1000.
    pareto = []
    for p in array_sorted:
        if p[1] <  min_y:
            pareto.append((p[0],p[1]))
            min_y = p[1]

    return pareto

def get_pareto_front_from_files(configs):
    solutions = [[],[]]
    for f in configs.input:
        generation, o1, o2 = parse_file(f)

        # Generation should preferably be an empty list
        if generation:
            # Otherwise, only get the values from the last generation
            last_idx = generation.index(generation[-1])
            o1 = o1[last_idx:]
            o2 = o2[last_idx:]

        solutions[0] += o1
        solutions[1] += o2

    return get_pareto_front_from_array(np.array(solutions).T)

if __name__ == '__main__':
    from parameters import configs
    random.seed(configs.seed)

    get_pareto_front_from_files(configs)


