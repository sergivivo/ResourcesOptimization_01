import numpy as np
import random
import datetime
from file_utils import parse_file, get_solution_array

from pymoo.indicators.gd  import GD
from pymoo.indicators.igd import IGD
from pymoo.indicators.hv  import HV

#from analyze_functions import S, STE

def S(pf=None):
    def indicator(solution):
        n = len(solution)
        d_arr = np.array([
                min([
                        np.linalg.norm(x-y)
                        for x in solution
                        if not np.array_equal(x, y)
                    ])
                for y in solution
            ])

        d_mean = np.average(d_arr)

        return np.sqrt(sum([(d_arr[i]-d_mean)**2 for i in range(n)]) / n)
    
    # Just as a way to give same format as other indicator functions
    return indicator

def STE(pf=None):
    def indicator(solution):
        # Spacing
        n = len(solution)
        d_arr = np.array([
                min([
                        np.linalg.norm(x-y)
                        for x in solution
                        if not np.array_equal(x, y)
                    ])
                for y in solution
            ])

        d_mean = np.average(d_arr)

        spacing = sum([(d_arr[i] - d_mean)**2 for i in range(n)]) / (n-1)

        # Extent (considering there are only two objectives)
        f_min = np.array([
                min([
                        solution[i,j]
                        for i in range(solution.shape[0])
                    ])
                for j in range(solution.shape[1])
            ])

        f_max = np.array([
                max([
                        solution[i,j]
                        for i in range(solution.shape[0])
                    ])
                for j in range(solution.shape[1])
            ])

        extent = np.sum(np.abs(f_max - f_min))

        return spacing / extent

    # Just as a way to give same format as other indicator functions
    return indicator

def mean_time(date_a, time_a):
    FORMAT_STR = '%Y-%m-%d %H:%M:%S.%f'
    acc = 0.
    next_dt = datetime.datetime.strptime(
            '{} {}'.format(date_a[0], time_a[0]),
            FORMAT_STR
        )
    for date, time in zip(date_a, time_a):
        prev_dt = next_dt
        next_dt = datetime.datetime.strptime(
                '{} {}'.format(date,time),
                FORMAT_STR
            )
        acc += (next_dt - prev_dt).total_seconds()

    return acc / (len(date_a) - 1)

def solutions():
    pass

INDICATORS = {
    'GD': GD,
    'IGD': IGD,
    'HV': HV,
    'S': S,
    'STE': STE
}

def get_table(configs):
    n_obj = configs.n_objectives

    alg_solutions = []
    alg_ts_dates = []
    alg_ts_times = []
    for f in configs.input:
        ts_date_a, ts_time_a, solutions = get_solution_array(f, n_obj=n_obj, timestamps=True)
        alg_solutions.append([
                np.unique(s, axis=0) for s in solutions
            ]) # filter repeated results
        alg_ts_dates.append(ts_date_a)
        alg_ts_times.append(ts_time_a)

    alg_names = configs.alg_names if configs.alg_names else []
    alg_names += [''] * (len(alg_solutions) - len(alg_names))

    #pf = np.unique(np.array(configs.ref_points), axis=0)
    pf = np.zeros((1, n_obj))

    # Values needed for normalization
    if not configs.network:
        o_min = np.array([
                min([
                    np.min(g[:,o])
                    for s in alg_solutions
                    for g in s
                ])
                for o in range(n_obj)
            ])

        o_max = np.array([
                max([
                    np.max(g[:,o])
                    for s in alg_solutions
                    for g in s
                ])
                for o in range(n_obj)
            ])

    else:
        import pickle
        ntw = pickle.load(configs.network)

        o_min_lst, o_max_lst = [], []
        for o in range(n_obj):
            o_min_aux, o_max_aux = ntw.getObjectiveBounds(configs.objectives[o])
            o_min_lst.append(o_min_aux)
            o_max_lst.append(o_max_aux)

        o_min, o_max = np.array(o_min_lst), np.array(o_max_lst)

    # Normalization of everything
    for s in range(len(alg_solutions)): # for each algorithm given
        for g in range(len(alg_solutions[s])): # for each generation
            for o in range(n_obj):
                alg_solutions[s][g][:,o] = \
                        (alg_solutions[s][g][:,o] - o_min[o]) / (o_max[o] - o_min[o])

    #for o in range(n_obj):
    #    pf[:,o] = (pf[:,o] - o_min[o]) / (o_max[o] - o_min[o])

    # Pymoo performance indicators
    string = '{: <15}'.format('Algorithm')

    gen_step = configs.gen_step
    if gen_step == 0:
        last_gen = True
    else:
        string += '{: <6}'.format('Gen')
        last_gen = False

    string += '{: <15}'.format('Mean_time')
    string += '{: <15}'.format('Solutions')

    for name in INDICATORS.keys():
        string += '{: <15}'.format(name)

    string += '\n'

    for alg_n, alg_s, alg_tsd, alg_tst in zip(alg_names, alg_solutions, alg_ts_dates, alg_ts_times):
        if last_gen:
            gen_step = len(alg_s)

        for gen in range((len(alg_s)-1) % gen_step, len(alg_s), gen_step):
            string += '{: <15}'.format(alg_n)
            if not last_gen:
                string += '{: <15}'.format(gen+1)

            string += '{: <15}'.format('{:.10f}'.format(mean_time(alg_tsd, alg_tst)))
            string += '{: <15}'.format('{:.3f}'.format(len(alg_s[gen])))
            for name, ind_c in INDICATORS.items():
                #print(name)
                if name == 'HV':
                    ind = ind_c(np.ones((n_obj)))
                else:
                    # GD and IGD uses Pareto front
                    ind = ind_c(pf)
                solution = ind(alg_s[gen])
                string += '{: <15}'.format('{:.10f}'.format(solution))
            string += '\n'

    return string

if __name__ == '__main__':
    from parameters import configs

    print(get_table(configs))


