import networkx as nx


# Colormap used to map states to node colors
state_cmap = {'unknown': '#7f7f7f',            # middle gray
              'active': '#1f77b4',             # muted blue
              'good': '#2ca02c',               # cooked asparagus green
              'needs calibration': '#ff7f0e',  # safety orange
              'bad': '#d62728',                # brick red
              }


def get_state_col_map(snapshot):
    """
    Creates a dictionary with node names as keys and their state dependent
    color as item.
    """
    col_map = {}
    for node in snapshot['nodes'].values():
        col_map[node['name']] = \
            state_cmap[node['parameters']['state']['value']]

    return col_map


def snapshot_to_nxGraph(snapshot):
    """
    Creates a networkx graph object from a snapshot of a graph.
    This is mostly used for determining positions of the nodes required for
    plotting.
    """
    g_snap = snapshot['nodes']
    nxG = nx.DiGraph()
    nxG.add_nodes_from(g_snap)
    for node_name, n_snap in g_snap.items():
        for dependency in n_snap['parameters']['parents']['value']:
            nxG.add_edge(node_name, dependency)
    return nxG


def draw_graph_mpl(snapshot, pos=None, layout='spring'):
    """
    Function to create a quick plot of a graph using matplotlib.
    Intended mostly for for debugging purposes
    Args:
        snapshot
        layout (str) : layout to position the nodes options are:
            spring, shell, spectral and circular.
    returns:
        pos

    """
    nxG = snapshot_to_nxGraph(snapshot)
    if pos is None:
        if layout == 'spring':
            pos = nx.spring_layout(nxG, iterations=5000)
        elif layout == 'shell':
            pos = nx.shell_layout(nxG)
        elif layout == 'spectral':
            pos = nx.spectral_layout(nxG)
        elif layout == 'circular':
            pos = nx.circular_layout(nxG)
        else:
            raise ValueError('layout not recognized')

    # Edge colors need to be set using a value mapping and a cmap

    cm = get_state_col_map(snapshot)
    colors_list = [cm[node] for node in nxG.nodes()]

    nx.draw_networkx_nodes(nxG, pos, node_color=colors_list)
    # Arrows look pretty bad
    nx.draw_networkx_edges(nxG, pos, arrows=True)
    nx.draw_networkx_labels(nxG, pos)
    return pos
