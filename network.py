import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import random

from ntw_functions import barabasi_albert_weighted_graph, get_pareto_distribution, truncate_array
from ntw_classes import Node, User, Task


# CLASSES
# ==============================================================================
class Network:
    """
    This class will manage the network with all the tasks, users, nodes and
    the graph resulting of the connection between these nodes. It will also
    give valuable information needed for the optimizations.
    """
    def __init__(self, conf):
        self.seed = conf.seed
        np.random.seed(conf.seed)
        
        # Generate the graph
        self.graph = barabasi_albert_weighted_graph(seed=conf.seed, n=conf.n_nodes, m=conf.edges, maxw=conf.max_weight, minw=conf.min_weight)

        # Betweenness centrality
        btw_cnt = nx.betweenness_centrality(self.graph, seed=conf.seed)
        # https://networkx.org/documentation/networkx-1.10/reference/generated/networkx.algorithms.centrality.betweenness_centrality.html
        bc_sorted = sorted(btw_cnt.items(), reverse=True, key=lambda e: e[1])

        # Memory for each node
        self.memory = truncate_array(
            get_pareto_distribution(
                conf.node_memory_pareto_shape, 
                conf.n_nodes,
                conf.node_memory_choice[0]),
            step_array=np.array(
                conf.node_memory_choice))

        self.memory = np.sort(self.memory)[::-1]

        self.nodes = [
            Node(
                max_tasks = random.choice(conf.node_max_tasks_choice)
            ) for _ in range(conf.n_nodes)]

        # Assign memory to each node depending on its centrality giving more
        # memory to the nodes that have more betweenness centrality
        #np.random.shuffle(self.memory)
        for i, _ in bc_sorted:
            self.nodes[i].memory = self.memory[i]

        # Generate the management data for the services while also randomly
        # assigning these services to a single user. Servers for these tasks
        # will be assigned case by case depending on the optimization tasks.
        self.tasks = [
            Task(
                memory = round(
                    get_pareto_distribution(
                        conf.task_memory_pareto_shape, 1, conf.task_min_memory,
                    ).clip(max=conf.task_max_memory)[0], 2),
                user_id = random.randrange(conf.n_users) # TODO: remove
            ) for _ in range(conf.n_tasks)]

        # Generate the management data for the users
        self.users = [User() for _ in range(conf.n_users)]
        self._addUsers(conf.min_weight, conf.max_weight)

        # Generate the user access to each service. A user can access many
        # services and a service can be accessed by many users, so the resulting
        # datastructure is a set of pairs of tasks/users.
        tu_matrix = self._generateTaskUserAssignmentMatrix_v2(p=conf.probability)
        self.task_user = np.transpose(np.nonzero(tu_matrix))

    def _addUsers(self, minw=0., maxw=1., roundw=1):
        """
        Add users as nodes of a graph. These nodes act in a different way than
        the server nodes. The users' ids start after last server's id.
        """
        n_nodes = len(self.nodes)
        n_users = len(self.users)

        # Assign a probability to each node depending on its degree of
        # centrality, giving more probability to nodes with less centrality
        bc = self.getBetweennessCentrality()
        maxv = max(bc.values())
        bc_prob = [(k, (maxv - v)/(maxv*n_nodes - maxv)) for (k, v) in bc.items()]

        for uid in range(n_nodes, n_nodes + n_users):
            # Get node's id given a random float
            acc_prob = 0
            p = random.random()
            for i in range(n_nodes):
                acc_prob += bc_prob[i][1]
                if p < acc_prob:
                    break

            nid = bc_prob[i][0]

            self.graph.add_node(uid)
            self.graph.add_edge(uid, nid, weight=round(random.uniform(minw, maxw), roundw))

    def _generateTaskUserAssignmentMatrix_v1(self):
        """
        Old method: this randomly generates the matrix with 0.5 probability
        for each matrix cell to be 0 or 1 and retries until every service is
        requested by at least one user and every user requests at least one
        service. Less efficient than the second version.
        """
        tu_matrix = np.random.choice([0,1], (len(self.tasks), len(self.users)))
        while not np.all(np.any(tu_matrix, 0)) or not np.all(np.any(tu_matrix, 1)):
            tu_matrix = np.random.choice([0,1], (len(self.tasks), len(self.users)))
            # Ensure that each user requests at least one task and each tasks is
            # requested by at least one user.
        return tu_matrix

    def _generateTaskUserAssignmentMatrix_v2(self, p=0.5):
        """
        DESCRIPTION OF THE PROCESS:
            1. Generate the Eye matrix (n×m):

                1 0 0 0 0
                0 1 0 0 0
                0 0 1 0 0
                0 0 0 1 0
                0 0 0 0 1
                0 0 0 0 0
                0 0 0 0 0
                0 0 0 0 0

            2. If rows > cols, then place a random one each row (after the
                square submatrix), else if cols > rows, do same on each column:

                1 0 0 0 0
                0 1 0 0 0
                0 0 1 0 0    Identity submatrix
                0 0 0 1 0
                0 0 0 0 1
                --------------------------------------------
                0 0 0 0 1
                1 0 0 0 0    Extra rows (or cols if m > n)
                0 1 0 0 0 

                - Notice: number of ones is equal to n

            3. Shuffle rows (shuffle cols if m > n)
                
                0 1 0 0 0
                0 0 0 0 1
                0 1 0 0 0
                1 0 0 0 0
                0 0 0 1 0
                0 0 0 0 1
                1 0 0 0 0
                0 0 1 0 0

            4. Add extra ones. Requires to calculate a new probability based
                on the amount of ones that are already placed.

                - Let p   := probability that an user requests a service
                - Let p_c := new probability given that n services are already
                             assigned (or m if m > n)
                - Let a   := remaining assignments needed

                If we treat p as the proportion of ones, we have:

                    n*m*p = n + a
                    n*m*p - n = a
                    n(m*p - 1) = a

                Then, we iterate over the zeros of the matrix and assign ones
                given the following probability:

                    p_c = a/(n*m - n) = n(m*p - 1) / n(m-1) = (m*p-1)/(m-1)

                If m > n, we change m for n

        """
        # Eye matrix
        n, m = len(self.tasks), len(self.users)
        tu_matrix = np.eye(n, m, dtype=np.uint8)

        if n >= m:
            # Set ones randomly remaining rows
            for i in range(m, n):
                tu_matrix[i, random.randrange(m)] = 1

            # Shuffle rows
            np.random.shuffle(tu_matrix)
            if m == 1:
                return tu_matrix
            p_c = (m*p-1)/(m-1)

        else:
            # Set ones randomly remaining columns
            for i in range(n, m):
                tu_matrix[random.randrange(n), i] = 1

            # Shuffle columns
            np.random.shuffle(tu_matrix.T)
            if n == 1:
                return tu_matrix
            p_c = (n*p-1)/(n-1)

        # Set remaining ones randomly according to new probability
        if p_c > 0.:
            for i in range(n):
                for j in range(m):
                    if tu_matrix[i,j] == 0 and random.random() < p_c:
                        tu_matrix[i,j] = 1

        return tu_matrix


    def displayGraph(self, seed=1):
        """
        Display the resulting graph of the network with the server nodes,
        users and the weights of the connections. Green nodes represent the
        server nodes, while red nodes represent the users. User's ids start
        after last server node id.
        """
        plt_gnp = plt.subplot(1,1,1)

        pos = nx.spring_layout(self.graph, seed=seed)
        color = ['lime' if node < len(self.nodes) else 'red' for node in self.graph]
        nlabels = {
                i:'{}{}'.format(
                    'N' if i < len(self.nodes) else 'U',
                    i if i < len(self.nodes) else i - len(self.nodes))
                for i in range(len(self.nodes) + len(self.users))
            }
        nx.draw_networkx(self.graph, pos, labels=nlabels, font_size=8, font_weight='bold', node_color=color)

        elabels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=elabels)

        plt.show()

    # GETTERS
    # ==========================================================================

    # Values
    def getNodeOccupiedMemory(self, node_id):
        """Get node's available memory considering the amount of tasks being
        executed on it"""
        total_task_mem = sum([t.memory for t in self.tasks if t.node_id == node_id])
        return total_task_mem

    def getNodeAvailableMemory(self, node_id):
        return self.nodes[node_id].memory - getNodeOccupiedMemory(node_id)

    def getTotalNodeMemory(self):
        return np.sum(self.memory)

    def getTotalTaskMemory(self):
        return np.sum([t.memory for t in self.tasks])

    def getNUsers(self):
        return len(self.users)

    def getNNodes(self):
        return len(self.nodes)

    def getNTasks(self):
        return len(self.tasks)

    def getMinimumNNodesNeeded(self):
        """Calculates the hipotetical minimum number of nodes needed for
        holding all the services. This method uses the sorted node memory array
        and keeps adding node memory until the sum of the memory of all
        services can be stored. Notice this is not necessarily true, as
        services' required memory cannot be splited between nodes. Just useful
        for calculating the normalized value of f2."""

        total_task_mem = np.sum([t.memory for t in self.tasks])
        total_node_mem = 0.
        nodes_needed = 0
        while total_node_mem <= total_task_mem and nodes_needed < len(self.nodes):
            total_node_mem += self.memory[nodes_needed]
            nodes_needed += 1

        return nodes_needed

    def getTasksAverageDistanceToUser(self, matrix, undm=None, tuam=None, maximize=False):
        """
        Returns a float with the average distance of all services to
        their respective users.

        Acronyms:
        - tnam: task/node assignment matrix
        - undm: user/node distance matrix
        - tuam: task/user assignment matrix
        - tudm: task/user distance matrix

        Matrices tuam and undm can be passed by parameter for efficiency
        purposes.
        """

        if tuam is None: tuam = self.getTaskUserAssignmentMatrix()
        tudm = self.getTaskUserDistanceMatrix(
                matrix, undm=undm, tuam=tuam, includeAll=False, maximize=maximize)

        tua_sum = np.sum(tudm, axis=1) 
        tud_sum = np.sum(tuam, axis=1)
        tu_filter = (tua_sum != 0) # Filter so that there's no division by zero

        avg_row = tua_sum[tu_filter] / tud_sum[tu_filter]
        return np.average(avg_row)

    def getTasksMinAverageDistanceToUser(self, undm=None, tuam=None):
        """
        Returns a float with the max possible average distance of all services
        to their respective users. This is achieved by passing tnam as a full
        matrix of ones, so it will traverse all nodes for each service getting
        the minimum distance.

        This method is useful for getting the normalized value of f1.
        """
        tnam = np.ones((len(self.tasks), len(self.nodes)), dtype=np.uint8)
        return self.getTasksAverageDistanceToUser(
                tnam, undm=undm, tuam=tuam)

    def getTasksMaxAverageDistanceToUser(self, undm=None, tuam=None):
        """
        Returns a float with the max possible average distance of all services
        to their respective users. This is achieved by passing tnam as a full
        matrix of ones, so it will traverse all nodes for each service getting
        the maximum distance.

        This method is useful for getting the normalized value of f1.
        """
        tnam = np.ones((len(self.tasks), len(self.nodes)), dtype=np.uint8)
        return self.getTasksAverageDistanceToUser(
                tnam, undm=undm, tuam=tuam, maximize=True)

    def getTasksMinAverageDistanceToUser_v2(self, undm=None, tuam=None):
        return np.average(np.min(self.getTaskNodeDistanceMatrix(undm, tuam), axis=1))

    def getTasksMaxAverageDistanceToUser_v2(self, undm=None, tuam=None):
        return np.average(np.max(self.getTaskNodeDistanceMatrix(undm, tuam), axis=1))

    def getBetweennessCentrality(self):
        return nx.betweenness_centrality(
                self.graph.subgraph(range(len(self.nodes))),
                seed=self.seed)

    # Dataclasses
    def getUser(self, user_id):
        return self.users[user_id]

    def getNode(self, node_id):
        return self.nodes[node_id]

    def getTask(self, task_id):
        return self.tasks[task_id]

    # Lists
    def getUserList(self):
        return self.users

    def getTaskList(self):
        return self.tasks

    def getNodeList(self):
        return self.nodes

    def getUserTasks(self, user_id):
        """Get the list of tasks requested by an user."""
        return [t for t in self.tasks if t.user_id == user_id]
            
    def getNodeExecutingTasks(self, node_id):
        """Get the list of tasks assigned to a server node."""
        return [t for t in self.tasks if t.node_id == node_id]

    # NumPy 1D arrays
    def getTaskUserAssignmentArray(self):
        """ Given that a task can only be assigned to an user, we can simplify
        the operations that retrieve this information """
        return np.array([t.user_id for t in self.tasks])

    def getTaskNodeAssignmentArray(self):
        """Given that a task can only be assigned to a node, we can simplify
        the operations that retrieve this information"""
        return np.array([t.node_id for t in self.tasks])

    def getTaskMemoryArray(self):
        return np.array([t.memory for t in self.tasks])


    def getNodeMemoryArray(self):
        return np.array([n.memory for n in self.nodes])


    def getNodeOccupiedMemoryArray(self, m=None):
        tn_nonzeros = np.nonzero(m)
        mem_array = np.zeros(len(self.nodes))
        for i in range(len(tn_nonzeros[0])):
            tid = tn_nonzeros[0][i]
            nid = tn_nonzeros[1][i]
            mem_array[nid] += self.tasks[tid].memory

        return mem_array

    def getNodeAvailableMemoryArray(self, m=None):
        if m is not None:
            capacity = self.getNodeMemoryArray()
            occupied = self.getNodeOccupiedMemoryArray(m)
            return capacity - occupied
        else:
            # Not implemented
            return np.array([])
    
    def getTaskDistanceArray(self, m):
        """Returns distances of tasks to their respective users given a
        task/node assignment matrix"""
        tu_assign_m = self.getTaskUserAssignmentMatrix()
        un_dist_m   = self.getUserNodeDistanceMatrix()

        # Find ones of task/node matrix
        tn_nonzeros = np.nonzero(m)

        # Find ones of task/user matrix
        tu_nonzeros = np.nonzero(tu_assign_m)

        tasks = np.zeros(len(self.tasks), np.float64)
        for i in range(len(tn_nonzeros[0])):
            tid = tn_nonzeros[0][i]
            x = np.where(tu_nonzeros[0] == tid)
            for uid in x:
                # this for is needed when a task is assigned to more than one user
                tasks[tid] += un_dist_m[tu_nonzeros[1][uid], tn_nonzeros[1][i]]

        return tasks

    # NumPy matrices
    def getTaskUserAssignmentMatrix(self):
        tu_assign_m = np.zeros((len(self.tasks), len(self.users)), np.uint8)
        for t,u in self.task_user:
            tu_assign_m[t,u] += 1
        return tu_assign_m

        """
        Old solution:

        Given that a task can only be assigned to an user, we can simplify
        the operations that retrieve this information.

        assignment = np.zeros((len(self.tasks), len(self.users)), dtype=np.int16)
        for t in self.tasks:
            assignment[t.id, t.user_id] += 1
        return assignment
        """

    def getUserNodeDistanceMatrix(self):
        """Get the distance matrix from the users (rows) to the server nodes
        (columns) using Dijkstra's algorithm."""
        distances = np.empty((len(self.users), len(self.nodes)))
        for uid in range(len(self.users)):
            dct = nx.single_source_dijkstra_path_length(self.graph, uid + len(self.nodes))
            for nid in range(len(self.nodes)):
                distances[uid, nid] = dct[nid]
        return distances
    
    def getTaskUserDistanceMatrix(self, tnam, undm=None, tuam=None, includeAll=True, maximize=False):
        """Get the distance matrix from the tasks (rows) to the users
        (columns) given a task/node assignment matrix

        Acronyms:
        - tnam: task/node assignment matrix
        - undm: user/node distance matrix
        - tuam: task/user assignment matrix
        - tudm: task/user distance matrix

        Parameter 'includeAll' means include unassigned task/user distances.
        If set to false, each unassigned element will contain a zero. Useful
        for calculating averages by adding elements by columns or rows.

        Parameter 'maximize', for multinode assignment, will take the node with
        the requested service that is further away from the user instead of the
        closer node. Useful for normalization.

        Matrices undm and tuam can be passed by parameter for efficiency
        purposes.
        """

        if undm is None: undm = self.getUserNodeDistanceMatrix()

        if not includeAll and tuam is None:
            # In order to know which to inclue or exclude (m[row,col] == 1)
            tuam = self.getTaskUserAssignmentMatrix()

        tudm = np.zeros((len(self.tasks), len(self.users)), np.float64)

        # Get tasks' and nodes' indexes of nonzero values in matrix
        tn_nonzeros = np.nonzero(tnam)

        for uid in range(len(self.users)):
            for i in range(len(tn_nonzeros[0])):
                tid = tn_nonzeros[0][i]
                nid = tn_nonzeros[1][i]
                if includeAll or tuam[tid, uid] == 1:
                    if not maximize:
                        # Will take the minimum value
                        if tudm[tid, uid] == 0:
                            tudm[tid, uid] = undm[uid, nid]
                        elif undm[uid, nid] < tudm[tid, uid]: 
                            tudm[tid, uid] = undm[uid, nid]
                    elif undm[uid, nid] > tudm[tid, uid]: 
                        # Will take the maximum value
                        tudm[tid, uid] = undm[uid, nid]


        return tudm

    def getTaskNodeAssignmentMatrix(self, array=None):
        """Get the matrix of the amount of instances of each task (rows) on each
        server node (columns) given an array of integers"""
        assignment = np.zeros((len(self.tasks), len(self.nodes)), dtype=np.int16)
        if array is not None:
            for tid in range(len(array)):
                if 0 <= array[tid]:
                    assignment[tid, array[tid]] += 1
        else:
            # Retrieve from tasks datastructure
            for t in self.tasks:
                assignment[t.id, t.node_id] += 1

        return assignment
    
    def getTaskNodeDistanceMatrix(self, undm=None, tuam=None):
        """Get the matrix of the average distance that a service can have to
        the users that requests it depending on the node that it is assigned"""
        if undm is None: undm = self.getUserNodeDistanceMatrix()
        if tuam is None: tuam = self.getTaskUserAssignmentMatrix()

        tua_sum = np.sum(tuam, axis=1)
        tndm = np.zeros((len(self.tasks), len(self.nodes)))

        for t in range(len(self.tasks)):
            for n in range(len(self.nodes)):
                tnd_sum = 0.0
                for u in range(len(self.users)):
                    tnd_sum += tuam[t][u] * undm[u][n]
                tndm[t][n] = tnd_sum / tua_sum[t]

        return tndm


    def getTaskNodeMemoryMatrix(self, m=None):
        """Returns a task/node memory matrix given a task/node assignment matrix"""
        mm = np.zeros((len(self.tasks), len(self.nodes)), dtype=np.float64)
        if m is not None:
            t_memory_v = self.getTaskMemoryArray()

            # Find node of each task
            tn_nonzeros = np.nonzero(m)

            for i in range(len(tn_nonzeros[0])):
                tid = tn_nonzeros[0][i]
                nid = tn_nonzeros[1][i]
                mm[tid, nid] += t_memory_v[tid]

        else:
            # Retrieve from tasks datastructure
            for t in self.tasks:
                mm[t.id, t.node_id] = t.memory
        
        return mm


    # MANAGEMENT
    # ==========================================================================

    def assignTask(self, task_id, node_id, fraction=1.):
        """Assign a task to a server node."""
        self.tasks[task_id].node_id = node_id
    
    def removeTask(self, task_id, node_id=-1):
        """Remove task from server node"""
        self.tasks[task_id].node_id = -1

    # FILES
    # ==========================================================================
    def export_gexf(self, path):
        nx.write_gexf(self.graph, path)

    # ANALYSIS
    # ==========================================================================
    def checkMemoryRequirements():
        return np.sum(self.memory) >= np.sum([t.memory for t in self.tasks])



if __name__ == '__main__':
    # Use 'generate' subparser for testing

    from parameters import configs
    random.seed(configs.seed)

    ntw = Network(configs)

    print(ntw.getTaskNodeDistanceMatrix())

    import time

    t0 = time.time()
    print(ntw.getTasksMinAverageDistanceToUser(), ntw.getTasksMaxAverageDistanceToUser())
    t1 = time.time()
    print(t1-t0)

    t0 = time.time()
    print(ntw.getTasksMinAverageDistanceToUser_v2(), ntw.getTasksMaxAverageDistanceToUser_v2())
    t1 = time.time()
    print(t1-t0)

    #print(ntw.getTaskUserAssignmentMatrix())
    #print(ntw.getUserNodeDistanceMatrix())
    #print(ntw.getTasksMinAverageDistanceToUser())
    #print(ntw.getTasksMaxAverageDistanceToUser())

    #matrix = np.zeros((configs.n_tasks, configs.n_nodes), np.uint8)
    #for row in range(configs.n_tasks):
    #    col = random.randrange(configs.n_nodes)
    #    matrix[row, col] = 1

    #tuam = ntw.getTaskUserAssignmentMatrix()
    #tudm = ntw.getTaskUserDistanceMatrix(matrix, includeAll=False)

    #tua_sum = np.sum(tudm, axis=1) 
    #tud_sum = np.sum(tuam, axis=1)
    #tu_filter = (tua_sum != 0) # Filter so that there's no division by zero


    #print(tuam)
    #print(tudm)
    #print()

    #print(tua_sum)
    #print(tud_sum)
    #print()

    #print(tua_sum[tu_filter])
    #print(tud_sum[tu_filter])
    #print()

    #avg_row = tua_sum[tu_filter] / tud_sum[tu_filter]

    #print(avg_row)
    #print()
    #
    #print(np.average(avg_row))
    #print()

    #capacity = ntw.getNodeMemoryArray()
    #occupied = ntw.getNodeOccupiedMemoryArray(matrix)
    #print(capacity)
    #print(occupied)
    #print()
    #print(ntw.getNodeAvailableMemoryArray(matrix))
    #print()

    #print('=====================================')
    #print('Testing task/user assignment function')
    #print('=====================================')
    #print()

    #print(ntw._generateTaskUserAssignmentMatrix_v2())


