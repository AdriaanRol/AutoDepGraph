import networkx as nx


def snapshot_to_nxGraph(snapshot):
    """
    Creates a networkx graph object from a snapshot of a graph.
    This is mostly used for determining positions of the nodes required for
    plotting.
    """
    g_snap = snapshot['nodes']
    nxG = nx.DiGraph()
    nxG.add_nodes_from(g_snap)
    print(list(g_snap.keys()))
    print(nxG.nodes())
    for node_name, n_snap in g_snap.items():
        for dependency in n_snap['parameters']['dependencies']['value']:
            nxG.add_edge(node_name, dependency)
    print(nxG.nodes())
    print(nxG.edges())
    return nxG


def draw_graph_mpl(snapshot):
    """
    Function to create a quick plot of a graph using matplotlib.
    Intended mostly for for debugging purposes
    """
    nxG = snapshot_to_nxGraph(snapshot)
    pos = nx.spring_layout(nxG)
    # Edge colors need to be set using a value mapping and a cmap
    nx.draw_networkx_nodes(nxG, pos, )  # node_color=)
    # Arrows look pretty bad
    nx.draw_networkx_edges(nxG, pos, arrows=True)
    nx.draw_networkx_labels(nxG, pos)
