from pymoo.core.problem import Problem, ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize

import numpy as np



class Problem01(ElementwiseProblem):
    """
    VARIABLES:
        - n×m variables enteras, posteriormente organizadas matricialmente,
          para la asignación de tareas (filas) a servidores (columnas).
    OBJETIVOS:
        - Reducir el número de servicios que hay en un nodo, es decir, la suma
          de las columnas tiene que dar valores pequeños. Minimizar promedio
          entre tareas asignadas a servidores
        - Reducir la distancia entre usuario y aplicación. Minimizar la suma de
          distancias de las tareas a sus respectivos usuarios.
    RESTRICCIONES:
        - Una tarea no puede estar asignada a más de un nodo, es decir, la suma
          de las filas de la matriz es 1.
        - Todas las tareas deben estar asignadas
        - Las tareas asignadas a un nodo no pueden superar su capacidad máxima
    RANGO:
        - Lower bound: 0
        - Upper bound: 1
    """

    def __init__(self, network):

        self.network = network

        self.N_TASKS = network.getNTasks()
        self.N_USERS = network.getNUsers()
        self.N_NODES = network.getNNodes()

        super().__init__(
                n_var = self.N_TASKS*self.N_NODES,
                n_obj = 2,
                n_ieq_constr = 3,
                xl = 0,
                xu = 1,
                vtype = int)

    def _getNodeAssignedMemory(self, m):
        # Find node of each task
        tn_nonzeros = np.nonzero(m)

        mm = np.zeros((self.N_TASKS, self.N_NODES))
        for i in range(len(tn_nonzeros[0])):
            tid = tn_nonzeros[0][i]
            nid = tn_nonzeros[1][i]
            mm[tid, nid] += self.t_memory_v[tid]
        
        return np.sum(mm, axis=0)

    def _evaluate(self, x, out, *args, **kwargs):
        matrix = x.reshape((self.N_TASKS, self.N_NODES))

        f1 = np.max(np.sum(matrix, axis=0)) # Minimizar número de tareas asignadas
                                            # a cada servidor
        f2 = np.sum(self.network.getTaskDistanceArray(matrix)) # Minimizar suma de distancias de tareas

        g1 = np.max(np.sum(matrix, axis=1)) - 1 # Solo puede haber un nodo por tarea
        g2 = 1 - np.min(np.sum(matrix, axis=1)) # Todas las tareas deben estar asignadas

        assigned_memory_v = np.sum(self.network.getTaskNodeMemoryMatrix(matrix), axis=0)
        g3 = np.max(assigned_memory_v - self.network.getNodeMemoryArray())
        # La memoria restante de cada servidor no puede ser menor a cero.
        # Dicho de otro modo, al restar la memoria ocupada con la capacidad,
        # debe ser menor o igual a cero

        out['F'] = [f1, f2]
        out['G'] = [g1, g2, g3]




if __name__ == '__main__':
    import random
    from parameters import configs
    from network import Network

    random.seed(727)

    ntw = Network(configs)

    problem = Problem01(ntw) # Insert a network object here

    algorithm = NSGA2(pop_size = 100,
        sampling=IntegerRandomSampling(),
        crossover=SBX(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
        mutation=PM(prob=1.0, eta=3.0, vtype=float, repair=RoundingRepair()),
        eliminate_duplicates=True
    )

    res = minimize(
        problem,
        algorithm,
        termination=('n_gen', 2000),
        seed=727,
        verbose=False
    )

    print(res.X[0])
    print(res.F)

