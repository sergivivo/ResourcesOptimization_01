from problems import Problem01v3, MySampling, MyCrossover, MyMutation, MyDuplicateElimination, MyRepair

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

    problem = Problem01v3(ntw)
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
        ref_points = np.array([[18., 6.], [15., 8.], [21., 5.]]) 

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
        ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=12)

        algorithm = NSGA3(pop_size = configs.pop_size,
            ref_dirs=ref_dirs,
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
        verbose=configs.verbose, save_history=configs.save_history
    )

    val = [e.opt.get('F') for e in res.history]

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

