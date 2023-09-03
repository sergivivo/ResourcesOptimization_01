from problems import Problem01v3
from problem_tools import MySampling, MyCrossover, MyRepair, MyMutation, MyDuplicateElimination, MyCallback

from pymoo.algorithms.moo.nsga2  import NSGA2
from pymoo.algorithms.moo.rnsga2 import RNSGA2
from pymoo.algorithms.moo.nsga3  import NSGA3
from pymoo.algorithms.moo.unsga3 import UNSGA3
from pymoo.algorithms.moo.rnsga3 import RNSGA3
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
        'CTAEA': CTAEA,
        'SMSEMOA': SMSEMOA,
        'RVEA': RVEA
    }

def solve(ntw, configs):

    if configs.algorithm in ('NSGA2', 'RNSGA2'):
        print("ERROR: Chosen algorithm does not support single-mode execution.")
        return None

    problem = Problem01v3(ntw, multimode=not configs.single_mode, l=configs.lmb)
    termination = get_termination(configs.termination_type, configs.n_gen)

    if configs.algorithm == 'NSGA2':
        algorithm = NSGA2(
                pop_size = configs.pop_size,
                sampling = MySampling(),
                crossover = MyCrossover(),
                mutation = MyMutation(configs.mutation_prob),
                repair = MyRepair(),
                callback = MyCallback(save_history=configs.save_history),
                eliminate_duplicates = MyDuplicateElimination()
            )

    elif configs.algorithm == 'SMSEMOA':
        algorithm = SMSEMOA(
                sampling=MySampling(),
                crossover=MyCrossover(),
                mutation=MyMutation(configs.mutation_prob),
                repair=MyRepair(),
                callback = MyCallback(save_history=configs.save_history),
                eliminate_duplicates=MyDuplicateElimination()
            )

    elif configs.algorithm in ('RNSGA2', 'RNSGA3'):
        # Algorithms that use reference points
        ref_points = np.array(configs.ref_points)

        if configs.algorithm == 'RNSGA2':
            algorithm = RNSGA2(
                    pop_size = configs.pop_size,
                    ref_points = ref_points,
                    sampling = MySampling(),
                    crossover = MyCrossover(),
                    mutation = MyMutation(configs.mutation_prob),
                    repair = MyRepair(),
                    callback = MyCallback(save_history=configs.save_history),
                    eliminate_duplicates = MyDuplicateElimination()
                )
        else:
            algorithm = RNSGA3(
                    pop_per_ref_point = configs.pop_size // ref_points.size,
                    ref_points = ref_points,
                    sampling = MySampling(),
                    crossover = MyCrossover(),
                    mutation = MyMutation(configs.mutation_prob),
                    repair = MyRepair(),
                    callback = MyCallback(save_history=configs.save_history),
                    eliminate_duplicates = MyDuplicateElimination()
                )
            

    else:
        # Algorithms that use reference directions
        ref_dirs = get_reference_directions(
                'das-dennis',
                1 if configs.single_mode else 2,
                n_partitions=configs.n_partitions
            )

        if configs.algorithm in ('CTAEA', 'RVEA'):
            # Algorithms without population size
            algorithm = algdict[configs.algorithm] (
                    ref_dirs = ref_dirs,
                    sampling = MySampling(),
                    crossover = MyCrossover(),
                    mutation = MyMutation(configs.mutation_prob),
                    repair = MyRepair(),
                    callback = MyCallback(save_history=configs.save_history),
                    eliminate_duplicates = MyDuplicateElimination()
                )
        else:
            # Algorithms with population size
            algorithm = algdict[configs.algorithm] (
                    pop_size = configs.pop_size,
                    ref_dirs = ref_dirs,
                    sampling = MySampling(),
                    crossover = MyCrossover(),
                    mutation = MyMutation(configs.mutation_prob),
                    repair = MyRepair(),
                    callback = MyCallback(save_history=configs.save_history),
                    eliminate_duplicates = MyDuplicateElimination()
                )

    res = minimize(
        problem,
        algorithm,
        termination=termination,
        seed=configs.seed,
        verbose=configs.verbose
    )

    if configs.save_history:
        return res.algorithm.callback.string_history
    else:
        return res.algorithm.callback.string_solution

