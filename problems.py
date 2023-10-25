from pymoo.core.problem   import Problem, ElementwiseProblem

from problem_tools import MySampling, MyCrossover, MyRepair, MyMutation, MyDuplicateElimination, MyCallback
from default import OBJ_LIST

from pymoo.termination import get_termination
from pymoo.algorithms.moo.nsga2  import NSGA2
from pymoo.optimize import minimize

import numpy as np
import random

import matplotlib.pyplot as plt


class Problem01v1(ElementwiseProblem):
    """
    VARIABLES:
        - n×m variables enteras, posteriormente organizadas matricialmente,
          para la asignación de tareas (filas) a servidores (columnas).
    OBJETIVOS:
        - Minimizar el número de nodos que tienen al menos una tarea
        - Reducir la distancia entre usuario y aplicación. Minimizar la suma de
          distancias de los usuarios que acceden a cada servicio.
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

        f1 = self.network.getTasksAverageDistanceToUser(matrix)
        f2 = np.count_nonzero(np.max(matrix, axis=0))

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
        - Minimizar el número de nodos que tienen al menos una tarea
        - Reducir la distancia entre usuario y aplicación. Minimizar el
          promedio de distancias de los usuarios que acceden a cada servicio.
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

        f1 = self.network.getTasksAverageDistanceToUser(matrix)
        f2 = np.count_nonzero(np.max(matrix, axis=0))

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
        - Minimizar el número de nodos que tienen al menos una tarea
        - Reducir la distancia entre usuario y aplicación. Minimizar la suma de
          distancias de los usuarios que acceden a cada servicio.
    RESTRICCIONES:
        - Las tareas asignadas a un nodo no pueden superar su capacidad máxima
        - Restricciones implícitas en el Sampling, Crossover y Mutation:
            - Una tarea no puede estar asignada a más de un nodo, es decir, la
              suma de las filas de la matriz es 1.
            - Todas las tareas deben estar asignadas

    Este problema exige la implementación de clases Sampling, Crossover y
    Mutation propias para la generación de matrices de NumPy.
    """

    def __init__(self, network, obj_list=OBJ_LIST[:2], multimode=True, l=0.5):

        self.network = network

        self.N_TASKS = network.getNTasks()
        self.N_USERS = network.getNUsers()
        self.N_NODES = network.getNNodes()

        self.multimode = multimode
        if type(l) == list:
            # lambda for converting bidimensional to single
            l = l[:len(obj_list)]
            if sum(l) > 1.:
                self.l = [l_elem / sum(l) for l_elem in l]

            if len(l) == len(obj_list):
                self.l = l
            else:
                self.l = l + [1.-sum(l)] + [0.] * (len(obj_list)-len(l)-1)
        else:
            if l > 1.:
                l = 1.

            if   len(obj_list) == 1:
                self.l = [l]
            elif len(obj_list) > 1:
                self.l = [l, 1.-l] + [0.] * (len(obj_list)-2)

        # Save for efficiency purposes
        self.undm = network.getUserNodeDistanceMatrix()
        self.unhm = network.getUserNodeHopsMatrix()
        self.tuam = network.getTaskUserAssignmentMatrix()

        # Values needed for normalization
        self.obj_list = obj_list
        self.f_min_list = []
        self.f_max_list = []
        for obj in obj_list:
            if   obj == OBJ_LIST[0]:
                self.f_min_list.append(
                        network.getTasksMinAverageDistanceToUser_v2(
                                undm=self.undm, tuam=self.tuam))
                self.f_max_list.append(
                        network.getTasksMaxAverageDistanceToUser_v2(
                                undm=self.undm, tuam=self.tuam))

            elif obj == OBJ_LIST[1]:
                self.f_min_list.append(network.getMinimumNNodesNeeded())
                self.f_max_list.append(self.N_NODES)

            elif obj == OBJ_LIST[2]:
                self.f_min_list.append(
                        network.getTasksMinAverageHopsToUser(
                                unhm=self.unhm, tuam=self.tuam))
                self.f_max_list.append(
                        network.getTasksMaxAverageHopsToUser(
                                unhm=self.unhm, tuam=self.tuam))

            if self.f_min_list[-1] == self.f_max_list[-1]:
                self.f_max_list += 1
                # This way, we avoid dividing by 0 and enforce 0 as normalized O2
                # value, so it does not interfere with O1 in any way

        super().__init__(
                n_var = 1,
                n_obj = len(self.obj_list) if multimode else 1,
                n_ieq_constr = 1)

    def _evaluate(self, x, out, *args, **kwargs):
        matrix = x[0]

        f_original = []
        f_norm = []
        for obj, f_min, f_max in zip(self.obj_list, self.f_min_list, self.f_max_list):
            if   obj == OBJ_LIST[0]:
                f = self.network.getTasksAverageDistanceToUser(
                        matrix, tuam=self.tuam, undm=self.undm)

            elif obj == OBJ_LIST[1]:
                f = np.count_nonzero(np.max(matrix, axis=0))

            elif obj == OBJ_LIST[2]:
                f = self.network.getTasksAverageHopsToUser(
                                matrix, tuam=self.tuam, unhm=self.unhm)
            
            f_original.append(f)
            f_norm.append((f - f_min) / (f_max - f_min))

        assigned_memory_v = np.sum(self.network.getTaskNodeMemoryMatrix(matrix), axis=0)
        g1 = np.max(assigned_memory_v - self.network.getNodeMemoryArray())
        # La memoria restante de cada servidor no puede ser menor a cero.
        # Dicho de otro modo, al restar la memoria ocupada con la capacidad,
        # debe ser menor o igual a cero

        if self.multimode:
            out['F'] = f_norm
            out['F_original'] = f_original
        else:
            out['F'] = sum([l*f for l, f in zip(self.l, self.f_norm)])
            out['F_original'] = f_original

        out['G'] = [g1]




# Testing
def solveAndAddToPlot(problem, algorithm, termination, name, color):
    res = minimize(
        problem,
        algorithm,
        termination=termination,
        seed=configs.seed,
        verbose=True,
        save_history=False
    )

    #val = [e.opt.get('F') for e in res.history]

    plt.scatter(res.F[:, 0], res.F[:, 1], s=30, facecolors='none', edgecolors=color, label=name)


if __name__ == '__main__':
    from parameters import configs
    from network import Network
    from pymoo.algorithms.moo.nsga2  import NSGA2
    import pickle

    random.seed(configs.seed)

    ntw = pickle.load(configs.input)

    problem = Problem01v3(ntw)

    fig, ax = plt.subplots()

    termination = get_termination(configs.termination_type, configs.n_gen)

    ### ALGORITHMS ###

    # NSGA2
    algorithm = NSGA2(pop_size = configs.pop_size,
        sampling=MySampling(),
        crossover=MyCrossover(),
        mutation=MyMutation(configs.mutation_prob),
        eliminate_duplicates=MyDuplicateElimination()
    )

    solveAndAddToPlot(problem, algorithm, termination, 'NSGA2', 'red')

    """
    # RNSGA2 (Necesita el frente de Pareto real)
    ref_points = np.array([[18., 6.], [15., 8.], [21., 5.]]) 

    algorithm = RNSGA2(pop_size = configs.pop_size,
        ref_points=ref_points,
        sampling=MySampling(),
        crossover=MyCrossover(),
        mutation=MyMutation(configs.mutation_prob),
        eliminate_duplicates=MyDuplicateElimination()
    )

    solveAndAddToPlot(problem, algorithm, termination, 'RNSGA2', 'blue')

    # NSGA3
    ref_dirs = get_reference_directions('das-dennis', 2, n_partitions=12)

    algorithm = NSGA3(pop_size = configs.pop_size,
        ref_dirs=ref_dirs,
        sampling=MySampling(),
        crossover=MyCrossover(),
        mutation=MyMutation(configs.mutation_prob),
        eliminate_duplicates=MyDuplicateElimination()
    )

    solveAndAddToPlot(problem, algorithm, termination, 'NSGA3', 'green')
    """

    ### END ALGORITHMS ###

    ax.legend()
    plt.show()
