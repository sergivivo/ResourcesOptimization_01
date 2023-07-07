import networkx as nx
from itertools import combinations, groupby
import random

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

def add_users(G, users, minw=0., maxw=1., roundw=1):
    """
    Add users as nodes of a graph. These nodes act in a different way than
    the server nodes. The users' ids start after last server's id.
    """
    nodesl = len(G.nodes)
    for i in range(nodesl, nodesl + users):
        G.add_node(i)
        G.add_edge(i, random.randrange(nodesl), weight=round(random.uniform(minw, maxw), roundw))
