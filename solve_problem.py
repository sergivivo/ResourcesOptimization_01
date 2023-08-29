from problems import Problem01v3
from problem_tools import MySampling, MyCrossover, MyRepair, MyMutation, MyDuplicateElimination, MyCallback

from pymoo.algorithms.moo.nsga2  import NSGA2
from pymoo.algorithms.moo.rnsga2 import RNSGA2
from pymoo.algorithms.moo.nsga3  import NSGA3
from pymoo.algorithms.moo.unsga3 import UNSGA3
from pymoo.algorithms.moo.rnsga3 import RNSGA3
from pymoo.algorithms.moo.moead  import MOEAD
#from pymoo.algorithms.moo.age    import AGEMOEA
from pymoo.algorithms.moo.ctaea  import CTAEA
from pymoo.algorithms.moo.sms    import SMSEMOA
from pymoo.algorithms.moo.rvea   import RVEA 

from pymoo.termination import get_termination

from pymoo.operators.sampling.rnd    import IntegerRandomSampling
from pymoo.operators.crossover.sbx   import SBX
from pymoo.operators.mutation.pm     import PM

from pymoo.util.ref_dirs import get_reference_directions

from pymoo.optimize import minimize

import numpy as np

algdict = {
        'NSGA2': NSGA2,
        'RNSGA2': RNSGA2,
        'NSGA3': NSGA3,
        'UNSGA3': UNSGA3,
        'RNSGA3': RNSGA3,
        'MOEAD': MOEAD,
        'AGEMOEA': None,
        'CTAEA': CTAEA,
        'SMSEMOA': SMSEMOA,
        'RVEA': RVEA
    }

def solve(ntw, configs):

    problem = Problem01v3(ntw, multimode=False)
    termination = get_termination(configs.termination_type, configs.n_gen)

    if configs.algorithm == 'NSGA2':
        # NSGA2
        algorithm = NSGA2(pop_size = configs.pop_size,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'RNSGA2':
        # RNSGA2 (Necesita el frente de Pareto real)
        ref_points = np.array(configs.ref_points)

        algorithm = RNSGA2(pop_size = configs.pop_size,
            ref_points=ref_points,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'NSGA3':
        # NSGA3
        ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=configs.n_partitions)

        algorithm = NSGA3(pop_size = configs.pop_size,
            ref_dirs=ref_dirs,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'UNSGA3':
        # UNSGA3
        ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=configs.n_partitions)

        algorithm = UNSGA3(pop_size = configs.pop_size,
            ref_dirs=ref_dirs,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'RNSGA3':
        # RNSGA3
        ref_points = np.array(configs.ref_points)

        algorithm = RNSGA3(pop_size = configs.pop_size,
            ref_points=ref_points,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'MOEAD':
        # MOEAD
        ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=configs.n_partitions)

        algorithm = MOEAD(pop_size = configs.pop_size,
            ref_dirs=ref_dirs,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'CTAEA':
        # CTAEA
        ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=configs.n_partitions)

        algorithm = CTAEA(ref_dirs=ref_dirs,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'SMSEMOA':
        # SMSEMOA
        algorithm = SMSEMOA(sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    if configs.algorithm == 'RVEA':
        # RVEA
        ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=configs.n_partitions)

        algorithm = RVEA(ref_dirs=ref_dirs,
            sampling=MySampling(),
            crossover=MyCrossover(),
            mutation=MyMutation(configs.mutation_prob),
            repair=MyRepair(),
            eliminate_duplicates=MyDuplicateElimination()
        )

    res = minimize(
        problem,
        algorithm,
        termination=termination,
        seed=configs.seed,
        verbose=configs.verbose,
        save_history=configs.save_history
    )

    val = [e.opt.get('F_original') for e in res.history]

    if configs.print:
        for i in range(len(res.X)):
            print(f'Solution {i}:')
            print(res.X[i])
            print()
            print(res.F[i])
            print()

    if configs.save_history:
        return val
    else:
        return res.F

