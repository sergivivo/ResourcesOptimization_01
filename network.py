import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import random

from config import *
from ntw_functions import gnp_random_connected_graph_weighted, add_users
from ntw_classes import Node, User, Task

# CLASSES
# ==============================================================================
class Network:
    """
    This class will manage the network with all the tasks, users, nodes and
    the graph resulting of the connection between these nodes. It will also
    give valuable information needed for the optimizations.
    """
    def __init__(self):
        # Generate the graph
        self.graph = gnp_random_connected_graph_weighted(N_NODES, P, MIN_WEIGHT, MAX_WEIGHT)
        add_users(self.graph, N_USERS, MIN_WEIGHT, MAX_WEIGHT)

        # Generate the management data for the servers
        self.nodes = [
                Node(
                    memory = random.choice(NODE_MEMORY_CHOICE),
                    max_tasks = random.choice(NODE_MAX_TASKS_CHOICE)
                ) for _ in range(N_NODES)]

        # Generate the management data for the users
        self.users = [User() for _ in range(N_USERS)]

        # Generate the management data for the services while also randomly
        # assigning these services to a single user. Servers for these tasks
        # will be assigned case by case depending on the optimization tasks.
        self.tasks = [
                Task(
                    memory = round(random.uniform(TASK_MIN_MEMORY, TASK_MAX_MEMORY), 2),
                    user_id = random.randrange(N_USERS)
                ) for _ in range(N_TASKS)]

    def displayGraph(self):
        """
        Display the resulting graph of the network with the server nodes,
        users and the weights of the connections. Green nodes represent the
        server nodes, while red nodes represent the users. User's ids start
        after last server node id.
        """
        plt_gnp = plt.subplot(1,1,1)

        pos = nx.spring_layout(self.graph)
        color = ['lime' if node < N_NODES else 'red' for node in self.graph]
        nlabels = {
                i:'{}{}'.format(
                    'N' if i < N_NODES else 'U',
                    i if i < N_NODES else i - N_NODES)
                for i in range(N_NODES + N_USERS)
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

    # NumPy arrays
    def getTaskMemoryArray(self):
        return np.array([t.memory for t in self.tasks])

    def getNodeMemoryArray(self):
        return np.array([n.memory for n in self.nodes])
    
    # NumPy matrices
    def getUserNodeDistanceMatrix(self):
        """Get the distance matrix from the users (rows) to the server nodes
        (columns) using Dijkstra's algorithm."""
        distances = np.empty((N_USERS, N_NODES))
        for uid in range(N_USERS):
            dct = nx.single_source_dijkstra_path_length(self.graph, uid + N_NODES)
            for nid in range(N_NODES):
                distances[uid, nid] = dct[nid]
        return distances
    
    def getTaskNodeAssignmentMatrix(self):
        """Get the matrix of the amount of instances of each task (rows) on each
        server node (columns)"""
        instances = np.zeros((N_TASKS, N_NODES), dtype=np.int16)
        for t in self.tasks:
            instances[t.id, t.node_id] += 1
        return instances

    def getTaskNodeMemoryMatrix(self):
        """Assuming each task can only be assigned to a single node, we can
        derive the following matrix"""
        memory = np.zeros((N_TASKS, N_NODES), dtype=np.float64)
        for t in self.tasks:
            memory[t.id, t.node_id] = t.memory
        return memory


    # MANAGEMENT
    # ==========================================================================

    def assignTask(self, task_id, node_id, fraction=1.):
        """Assign a task to a server node."""
        self.tasks[task_id].node_id = node_id
    
    def removeTask(self, task_id, node_id=-1):
        """Remove task from server node"""
        self.tasks[task_id].node_id = -1

