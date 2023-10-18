import numpy as np
import random
from file_utils import parse_file, get_solution_array

from pymoo.indicators.gd  import GD
from pymoo.indicators.igd import IGD
from pymoo.indicators.hv  import HV

#from analyze_functions import S, STE

def S(pf=None):
    def indicator(solution):
        n = len(solution)
        sol_ord = solution[
                np.lexsort((solution[:,1],solution[:,0]))
            ]
        d = np.zeros(len(solution), dtype=np.float64)
        for i in range(len(sol_ord)):
            d_min = 10000.

            # Check two nearest neighbours and get the smaller value
            if i-1 >= 0:
                d_new = np.linalg.norm(sol_ord[i] - sol_ord[i-1])
                if d_min > d_new:
                    d_min = d_new

            if i+1 < len(sol_ord):
                d_new = np.linalg.norm(sol_ord[i] - sol_ord[i+1])
                if d_min > d_new:
                    d_min = d_new

            d[i] = d_min

        d_mean = np.average(d)

        return np.sqrt(sum([(d[i]-d_mean)**2 for i in range(n)]) / n)
    
    # Just as a way to give same format as other indicator functions
    return indicator

def STE(pf):
    def indicator(solution):
        # Spacing
        n = len(solution)
        sol_ord = solution[
                np.lexsort((solution[:,1],solution[:,0]))
            ]
        d = np.zeros(len(solution), dtype=np.float64)
        for i in range(len(sol_ord)):
            d_min = 10000.

            # Check two nearest neighbours and get the smaller value
            if i-1 >= 0:
                d_new = np.linalg.norm(sol_ord[i] - sol_ord[i-1])
                if d_min > d_new:
                    d_min = d_new

            if i+1 < len(sol_ord):
                d_new = np.linalg.norm(sol_ord[i] - sol_ord[i+1])
                if d_min > d_new:
                    d_min = d_new

            d[i] = d_min

        d_mean = np.average(d)

        spacing = sum([(d[i]-d_mean)**2 for i in range(n)]) / (n-1)

        # Extent (considering there are only two objectives)
        f1_min, f1_max = np.min(solution[:,0]), np.max(solution[:,0])
        f2_min, f2_max = np.min(solution[:,1]), np.max(solution[:,1])
        extent = np.abs(f1_max - f1_min) + np.abs(f2_max - f2_min)

        return spacing / extent

    # Just as a way to give same format as other indicator functions
    return indicator

INDICATORS = {
    'GD': GD,
    'IGD': IGD,
    'HV': HV,
    'S': S,
    'STE': STE
}


def get_table(configs):
    alg_solutions = []
    for f in configs.input:
        solutions = get_solution_array(f)
        alg_solutions.append([
                np.unique(s, axis=0) for s in solutions
            ]) # filter repeated results

    alg_names = configs.alg_names if configs.alg_names else []
    alg_names += [''] * (len(alg_solutions) - len(alg_names))

    pf = np.unique(np.array(configs.ref_points), axis=0)

    # Values needed for normalization
    if not configs.network:
        o1_min = min([np.min(g[:,0]) for s in alg_solutions for g in s])
        o2_min = min([np.min(g[:,1]) for s in alg_solutions for g in s])
        o1_max = max([np.max(g[:,0]) for s in alg_solutions for g in s])
        o2_max = max([np.max(g[:,1]) for s in alg_solutions for g in s])
    else:
        import pickle
        ntw = pickle.load(configs.network)
        o1_min = ntw.getTasksMinAverageDistanceToUser_v2()
        o1_max = ntw.getTasksMaxAverageDistanceToUser_v2()
        o2_min = ntw.getMinimumNNodesNeeded()
        o2_max = ntw.getNNodes()

    # Normalization of everything
    for s in range(len(alg_solutions)): # for each algorithm given
        for g in range(len(alg_solutions[s])): # for each generation
            alg_solutions[s][g][:,0] = \
                    (alg_solutions[s][g][:,0] - o1_min) / (o1_max - o1_min)
            alg_solutions[s][g][:,1] = \
                    (alg_solutions[s][g][:,1] - o2_min) / (o2_max - o2_min)

    pf[:,0] = (pf[:,0] - o1_min) / (o1_max - o1_min)
    pf[:,1] = (pf[:,1] - o2_min) / (o2_max - o2_min)

    # Pymoo performance indicators
    string = '{: <12}'.format('Algorithm')

    gen_step = configs.gen_step
    if gen_step == 0:
        last_gen = True
    else:
        string += '{: <6}'.format('Gen')
        last_gen = False

    for name in INDICATORS.keys():
        string += '{: <15}'.format(name)

    string += '\n'

    for alg_n, alg_s in zip(alg_names, alg_solutions):
        if last_gen:
            gen_step = len(alg_s)

        for gen in range((len(alg_s)-1) % gen_step, len(alg_s), gen_step):
            string += '{: <12}'.format(alg_n)
            if not last_gen:
                string += '{: <6}'.format(gen+1)
            for name, ind_c in INDICATORS.items():
                if name == 'HV':
                    ind = ind_c([1,1])
                else:
                    ind = ind_c(pf)
                solution = ind(alg_s[gen])
                string += '{: <15}'.format('{:.10f}'.format(solution))
            string += '\n'

    return string

if __name__ == '__main__':
    from parameters import configs

    print(get_table(configs))


