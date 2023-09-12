import networkx as nx
from itertools import combinations, groupby
import random
import numpy as np

def gnp_random_connected_graph_weighted(n, p, minw=0., maxw=1., roundw=1):
    """
    Generates a random undirected graph, similarly to an Erdős-Rényi 
    graph, but enforcing that the resulting graph is connected

    Source:
    https://stackoverflow.com/questions/61958360/how-to-create-random-graph-where-each-node-has-at-least-1-edge-using-networkx/61961881#61961881
    """
    edges = combinations(range(n), 2)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for _, node_edges in groupby(edges, key=lambda x: x[0]):
        node_edges = list(node_edges)
        random_edge = random.choice(node_edges)
        G.add_edge(*random_edge, weight=round(random.uniform(minw, maxw), roundw))
        for e in node_edges:
            if random.random() < p:
                G.add_edge(*e, weight=round(random.uniform(minw, maxw), roundw))
    return G

def barabasi_albert_weighted_graph(n, m, seed=None, minw=0., maxw=1., roundw=1):
    G = nx.barabasi_albert_graph(seed=seed, n=n, m=m)
    for orig, dest in G.edges():
        G[orig][dest]['weight'] = round(random.uniform(minw, maxw), roundw)
    return G

def add_users(G, users, minw=0., maxw=1., roundw=1):
    """
    Add users as nodes of a graph. These nodes act in a different way than
    the server nodes. The users' ids start after last server's id.
    """
    nodesl = len(G.nodes)
    for i in range(nodesl, nodesl + users):
        G.add_node(i)
        G.add_edge(i, random.randrange(nodesl), weight=round(random.uniform(minw, maxw), roundw))

def get_pareto_distribution(shape, size, mode):
    return (np.random.pareto(shape, size) + 1) * mode

def truncate_array(array, step_size=1, step_array=None):
    copy = array.copy()
    for i in range(array.size):
        j = 0
        if step_array is None:
            while array[i] > step_size * (j+1) and i < array.size:
                j += 1

            copy[i] = step_size * j
        else:
            while j + 1 < step_array.size and i < array.size and \
                    array[i] > step_array[j+1]:
                j += 1

            copy[i] = step_array[j]

    return copy

if __name__ == '__main__':
    t = get_pareto_distribution(0.8, 40, 30).clip(max=1500.)
    for e in t:
        print(e)

    print()

    n = truncate_array(get_pareto_distribution(1.16, 20, 512), step_array=np.array([
        512, 1024, 2048, 4096]))
    for e in n:
        print(e)

    print(np.sum(t), np.sum(n))

