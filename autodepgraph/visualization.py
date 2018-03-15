import networkx as nx
import numpy as np
from autodepgraph.pg_visualization.pg_remotegraph import pg_DiGraph_window

# Colormap used to map states to node colors
state_cmap = {#'unknown': '#7f7f7f',            # middle gray
              'unknown': '#D3D3D3',            # light gray
              'active': '#1f77b4',             # muted blue
              'good': '#2ca02c',               # cooked asparagus green
              'needs calibration': '#ff7f0e',  # safety orange
              'bad': '#d62728',                # brick red
              }

# symbol map
pyqtgraph_symbol_map = {'normal': 'o',              # a circle
                        'manual_cal': 'h', }        # a hexagon

dot_type_symbol_map = {'normal': 'circle',              # a circle
                       'manual_cal': 'hexagon', }        # a hexagon



def get_state_col_map(snapshot):
    """
    Creates a dictionary with node names as keys and their state dependent
    color as value.
    """
    col_map = {}
    for node in snapshot['nodes'].values():
        col_map[node['name']] = \
            state_cmap[node['parameters']['state']['value']]
    return col_map


def get_type_symbol(node_snap, type_symbol_map: dict=pyqtgraph_symbol_map):
    """
    Get the symbol to represent specific node based on a symbol map.
    Note that this dict is different dependent on the desired output format

    e.g., matplotlib and pyqtgraph use "o" for circle but .dot uses "circle".
    """
    if (node_snap['parameters']['calibrate_function']['value']
            == 'NotImplementedCalibration'):
        state = 'manual_cal'
    else:
        state = 'normal'
    return type_symbol_map[state]

def get_type_symbol_map(graph_snapshot):
    """
    Returns a dictionary with node names as keys and a type dependent symbol
    as value.

    Currently there is only a distinction between "normal" nodes and
    "manual_cal" nodes. "manual_cal" nodes are those nodes that do not have
    a calibrate function specified and as such need to be set by hand.
    Normal nodes are all other nodes.
    """
    symb_map = {}
    for node in graph_snapshot['nodes'].values():
        symb_map[node['name']] = get_type_symbol(node, type_symbol_map=pyqtgraph_symbol_map)
    return symb_map


def get_attr_dict_from_node_snaphshot(node_snap):
    """
    Generates an attribute dictionary from a node snapshot.
    This is used when adding a node to a networkx graph.
    The attributes denote relevant meta data such as the state and
    the color to use when rendering the node.
    """
    state = node_snap['parameters']['state']['value']
    color = state_cmap[state]

    attr_dict = {'color': color,
                'fillcolor': color,
                'style': 'filled',
                'shape': get_type_symbol(node_snap,
                                         type_symbol_map=dot_type_symbol_map),
                'state': state,
                 'state': node_snap['parameters']['state']['value'],
                 'calibration_timeout': node_snap['parameters']['calibration_timeout']['value'],
                 'check_function': node_snap['parameters']['check_function']['value'],
              'calibrate_function': node_snap['parameters']['calibrate_function']['value'],
                }
    return attr_dict


def snapshot_to_nxGraph(snapshot, add_attributes:bool =True):
    """
    Creates a networkx graph object from a snapshot of a graph.

    This object can be used to create a dot
    """
    g_snap = snapshot['nodes']
    nxG = nx.DiGraph()
    if add_attributes:
        # Adds meta data used for generating the right figure
        # when a .dot renderer
        for node_name, node_snap in g_snap.items():
            attr_dict = get_attr_dict_from_node_snaphshot(node_snap)
            nxG.add_node(node_name, **attr_dict)
    else:
        nxG.add_nodes_from(g_snap)
    for node_name, n_snap in g_snap.items():
        for dependency in n_snap['parameters']['parents']['value']:
            nxG.add_edge(node_name, dependency)
    return nxG


def draw_graph_mpl(snapshot, pos=None):
    """
    Function to create a quick plot of a graph using matplotlib.
    Intended mostly for for debugging purposes
    Args:
        snapshot    snapshot snapshot of the graph
        pos         positions of the nodes
    returns:
        pos

    """
    nxG = snapshot_to_nxGraph(snapshot)
    if pos is None:
        pos = nx.spring_layout(nxG, iterations=5000)

    # Edge colors need to be set using a value mapping and a cmap

    cm = get_state_col_map(snapshot)
    colors_list = [cm[node] for node in nxG.nodes()]

    nx.draw_networkx_nodes(nxG, pos, node_color=colors_list)
    # Arrows look pretty bad
    nx.draw_networkx_edges(nxG, pos, arrows=True)
    nx.draw_networkx_labels(nxG, pos)
    return pos


def adjaceny_to_integers(nxG, pos_dict):
    """
    Helper function that takes a networkx graph object and returns the
    edges (adjacency) as an array of integers.

    Args:
        nxG : networkx graph object, contains the defined edges
        pos_dict : dictionary from the layout, contains the relevant order
            of the nodes
    returns:
        adj : array of integers specifying the edges
    """

    node_name_list = list(pos_dict.keys())
    adj = []
    for child, parent in nxG.edges():
        child_idx = node_name_list.index(child)
        parent_idx = node_name_list.index(parent)
        adj.append([child_idx, parent_idx])
    adj = np.array(adj)
    return adj


def draw_graph_pyqt(snapshot, DiGraphWindow=None, window_title=None):
    """


    Args:
        snapshot        : snapshot of the graph
        DiGraphWindow   : pyqtgraph remote graph window to be updated
            if None it will create a new plotting window to update
        window_title    : title of the plotting window
    returns:
        DiGraphWindow

    """
    if isinstance(snapshot, nx.DiGraph):
        nxG = snapshot

        # Converts it to an array to work with pyqtgraph plotting class
        pos_dict = nx.nx_agraph.graphviz_layout(nxG, prog='dot')

        colors_list = [state_cmap[node_dat['state']] for node_dat in
                   nxG.nodes.values()]
        symbols=['o']*len(colors_list)

    else:
        nxG = snapshot_to_nxGraph(snapshot, add_attributes=True)

        # Converts it to an array to work with pyqtgraph plotting class
        pos_dict = nx.nx_agraph.graphviz_layout(nxG, prog='dot')
        cm = get_state_col_map(snapshot)

        colors_list = [(cm[node]) for node in pos_dict.keys()]
        sm = get_type_symbol_map(snapshot)
        symbols = [(sm[node]) for node in pos_dict.keys()]

    pos = np.array(list(pos_dict.values()))
    adj = adjaceny_to_integers(nxG, pos_dict)
    labels = list(pos_dict.keys())

    if DiGraphWindow is None:
        DiGraphWindow = pg_DiGraph_window(window_title=window_title)

    DiGraphWindow.setData(pos=np.array(pos), adj=adj, size=20, symbol=symbols,
                          labels=labels, pen=(60, 60, 60),
                          symbolBrush=colors_list, pxMode=False)
    return DiGraphWindow



def draw_graph_svg(snapshot, filename: str):
    """
    Creates an svg using graphviz.

    If the file is saved to "autodepgraph/svg_viewer/adg_graph.svg" the
    realtime svg viewer can render it.
    """
    if isinstance(snapshot, nx.DiGraph):
        nxG = snapshot
    else:
        nxG = snapshot_to_nxGraph(snapshot, add_attributes=True)
    gvG = nx.nx_agraph.to_agraph(nxG)
    gvG.layout(prog='dot')
    gvG.draw(filename)


def write_graph_to_dotfile(snapshot, filename: str):
    nxG = snapshot_to_nxGraph(snapshot, add_attributes=True)
    nx.nx_agraph.write_dot(nxG, filename)

