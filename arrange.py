import numpy as np
import random
from file_utils import parse_file

# TODO: Arreglar para n dimensiones
def get_pareto_front_from_array(array, n_obj=2):
    keys = tuple([array[:, i] for i in range(n_obj-1, -1, -1)])
    idx_sorted = np.lexsort(keys)
    array_sorted = array[idx_sorted]

    max_o_n = [1000.] * n_obj
    pareto = []
    for p in array_sorted:
        any_o = False
        for i in range(1, n_obj):
            if p[i] < max_o_n[i]:
                any_o = True
        # any_o = o_1 < max_o_1 || o_2 < max_o_2 || ... || o_n < max_o_n

        if any_o:
            for i in range(1, n_obj):
                max_o_n[i] = p[i]
            pareto.append(p)

    return pareto

"""
# OLD ALGORITHM
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
"""


def get_pareto_front_from_files(configs, n_obj=2):
    solutions = [[] for _ in range(n_obj)]
    for f in configs.input:
        generation, o = parse_file(f, n_obj)

        # Generation should preferably be an empty list
        if generation:
            # Otherwise, only get the values from the last generation
            last_idx = generation.index(generation[-1])
            for i in range(n_obj):
                solutions[i] += o[i][last_idx:]

    return get_pareto_front_from_array(np.array(solutions).T, n_obj)

if __name__ == '__main__':
    from parameters import configs
    random.seed(configs.seed)

    get_pareto_front_from_array(array, n_obj=3)


