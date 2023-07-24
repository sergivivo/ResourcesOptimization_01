from pymoo.core.problem   import Problem, ElementwiseProblem
from pymoo.core.sampling  import Sampling
from pymoo.core.crossover import Crossover
from pymoo.core.mutation  import Mutation
from pymoo.core.duplicate import ElementwiseDuplicateElimination

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
from pymoo.operators.repair.rounding import RoundingRepair

from pymoo.optimize import minimize

import numpy as np
import random



class Problem01v1(ElementwiseProblem):
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



class Problem01v2(ElementwiseProblem):
    """
    VARIABLES:
        - n variables enteras, para la asignación de tareas a un servidor.
    OBJETIVOS:
        - Reducir el número de servicios que hay en un nodo, es decir, la suma
          de las columnas tiene que dar valores pequeños. Minimizar promedio
          entre tareas asignadas a servidores
        - Reducir la distancia entre usuario y aplicación. Minimizar la suma de
          distancias de las tareas a sus respectivos usuarios.
    RESTRICCIONES:
        - Todas las tareas deben estar asignadas (no -1)
        - Las tareas asignadas a un nodo no pueden superar su capacidad máxima
    RANGO:
        - Lower bound: -1
        - Upper bound: self.N_NODES - 1

    Esta solución simplifica la estructura de las variables de decisión. En
    lugar de emplear una matriz n×m de variables enteras para almacenar las
    asignaciones de tareas a nodos, dado a que una tarea sólo puede ser
    asignada a un nodo, podemos simplificar la estructura como un array 1D de
    Ids de nodos donde el índice se corresponde con la Id de la tarea asignada
    a dicho nodo.

        x = [-1, 4, 5, 2, 6, 2, 3]

        donde 'x[tid]' es la Id del nodo al que la tarea 'tid' ha sido asignada

    Para indicar que una tarea aún no ha sido asignada a ninguna tarea,
    empleamos el valor -1.
    """

    def __init__(self, network):

        self.network = network

        self.N_TASKS = network.getNTasks()
        self.N_USERS = network.getNUsers()
        self.N_NODES = network.getNNodes()

        super().__init__(
                n_var = self.N_TASKS,
                n_obj = 2,
                n_ieq_constr = 2,
                xl = -1,
                xu = self.N_NODES - 1,
                vtype = int)

    def _evaluate(self, x, out, *args, **kwargs):
        matrix = self.network.getTaskNodeAssignmentMatrix(x)

        f1 = np.max(np.sum(matrix, axis=0)) # Minimizar número de tareas asignadas
                                            # a cada servidor
        f2 = np.sum(self.network.getTaskDistanceArray(matrix)) # Minimizar suma de distancias de tareas

        g1 = - np.min(x) # Todas las tareas deben estar asignadas

        assigned_memory_v = np.sum(self.network.getTaskNodeMemoryMatrix(matrix), axis=0)
        g2 = np.max(assigned_memory_v - self.network.getNodeMemoryArray())
        # La memoria restante de cada servidor no puede ser menor a cero.
        # Dicho de otro modo, al restar la memoria ocupada con la capacidad,
        # debe ser menor o igual a cero

        out['F'] = [f1, f2]
        out['G'] = [g1, g2]



class Problem01v3(ElementwiseProblem):
    """
    VARIABLES:
        - 1 matriz de NumPy de n×m enteros, filas tareas y columnas nodos
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

    Este problema exige la implementación de clases Sampling, Crossover y
    Mutation propias para la generación de matrices de NumPy.
    """

    def __init__(self, network):

        self.network = network

        self.N_TASKS = network.getNTasks()
        self.N_USERS = network.getNUsers()
        self.N_NODES = network.getNNodes()

        super().__init__(
                n_var = 1,
                n_obj = 2,
                n_ieq_constr = 3)

    def _evaluate(self, x, out, *args, **kwargs):
        matrix = x[0]

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



class MySampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, 1),  None, dtype=object)
        for i in range(n_samples):
            matrix = np.zeros((problem.N_TASKS, problem.N_NODES), np.uint8)
            for row in range(problem.N_TASKS):
                col = random.randrange(problem.N_NODES)
                matrix[row, col] = 1

            X[i,0] = matrix

        return X

class MyCrossover(Crossover):
    def __init__(self):
        super().__init__(n_parents = 2, n_offsprings = 2)

    def _do(self, problem, X, **kwargs):
        n_parents, n_matings, n_var = X.shape[:3]
        Y = np.full_like(X, None, dtype=object)

        for k in range(n_matings):
            p1, p2 = X[0, k, 0], X[1, k, 0]
            off1, off2 = [], []

            for i in range(problem.N_TASKS):
                if random.random() < 0.5:
                    off1.append(p1[i])
                    off2.append(p2[i])
                else:
                    off1.append(p2[i])
                    off2.append(p1[i])

            Y[0, k, 0], Y[1, k, 0] = np.array(off1, np.uint8), np.array(off2, np.uint8)

        return Y

class MyMutation(Mutation):
    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        """Change the position of the 1 in a row"""
        for i in range(len(X)):
            for row in range(problem.N_TASKS):
                if random.random() < 0.01:
                    newcol = random.randrange(problem.N_NODES - 1)
                    for col in range(problem.N_NODES):
                        # Search one
                        if X[i, 0][row, col] == 1:

                            # New column choices before:
                            #               col
                            #                |
                            #                v
                            #   [0] [0] [0] [1] [0]  0

                            if newcol >= col:
                                newcol += 1

                            # New column choices now:
                            #               col
                            #                |
                            #                v
                            #   [0] [0] [0]  1  [0] [0]

                            X[i, 0][row, col] = 0
                            X[i, 0][row, newcol] = 1
                            break

        return X

class MyDuplicateElimination(ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return np.array_equal(a.X[0], b.X[0]) 


if __name__ == '__main__':
    from parameters import configs
    from network import Network

    random.seed(configs.seed)

    ntw = Network(configs)

    problem = Problem01v3(ntw)


    algorithm = NSGA2(pop_size = configs.pop_size,
        sampling=MySampling(),
        crossover=MyCrossover(),
        mutation=MyMutation(),
        eliminate_duplicates=MyDuplicateElimination()
    )

    
    """
    ref_points = np.array([[15., 120.], [6., 150.], [2., 240.]])

    algorithm = RNSGA2(pop_size = configs.pop_size,
        ref_points=ref_points,
        sampling=MySampling(),
        crossover=MyCrossover(),
        mutation=MyMutation(),
        eliminate_duplicates=MyDuplicateElimination()
    )
    """

    termination = get_termination(configs.termination_type, configs.n_gen)


    res = minimize(
        problem,
        algorithm,
        termination=termination,
        seed=configs.seed,
        verbose=True
    )


