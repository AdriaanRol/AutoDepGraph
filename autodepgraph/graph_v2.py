import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from autodepgraph.visualization import state_cmap

# Used to find functions in modules
from importlib import import_module
# Only used for finding instrument methods.
from qcodes.instrument.base import Instrument


class AutoDepGraph_DAG(nx.DiGraph):
    def __init__(self, name, cfg_plot_mode='matplotlib',
                 incoming_graph_data=None, **attr):
        """
        Directed Acyclic Graph used for calibrations.
        Inherits from a networkx DiGraph.

        The AutoDepGraph provides several constraints to nodes and edges
        as well as add the functionality to walk over the graph and visualize this.
        """
        attr['name'] = name
        attr['cfg_plot_mode'] = cfg_plot_mode

        super().__init__(incoming_graph_data, **attr)


    def add_node(self, node_for_adding, **attr):
        """
        """

        # there are set here to ensure these node attributes exist.
        # setting in this way will most likely interfere with joining multiple graphs
        attr['state'] = attr.get('calibration_timeout', 'unknown')
        attr['calibration_timeout'] = attr.get('calibration_timeout',
                                               np.inf)
        attr['calibrate_function'] = attr.get('calibrate_function',
            'autodepgraph.node_functions.calibration_functions'+
            '.NotImplementedCalibration')

        attr['check_function']= attr.get('check_function', 'autodepgraph.node_functions.check_functions'+
            '.always_needs_calibration')

        # TODO: support tolerance
        # attr['tolerance']= attr.get('tolerance', None)
        super().add_node(node_for_adding, **attr)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """
        Adds an edge that denotes a dependency in the calibration graph.
        u_of_edge -> v_of_edge denotes that u depends on v.
        """

        # Nodes must already exist to ensure they have the right properties
        assert u_of_edge in self.nodes()
        assert v_of_edge in self.nodes()
        super().add_edge( u_of_edge, v_of_edge, **attr)


    def execute_node(self, node, verbose=True):
        pass


    def check_node(self, node):
        pass

    def set_all_node_states(self, state):
        for node_dat in self.nodes.values():
            node_dat['state'] = state

    def draw_mpl(self, ax=None):
        if ax is None:
            f, ax = plt.subplots()
            ax.axis('off')
        ax.set_title(self.name)
        colors_list = [state_cmap[node_dat['state']] for node_dat in
            self.nodes.values()]
        pos = nx.nx_agraph.graphviz_layout(self, prog='dot')
        nx.draw_networkx_nodes(self, pos, ax=ax, node_color=colors_list)
        nx.draw_networkx_edges(self, pos, ax=ax, arrows=True)
        nx.draw_networkx_labels(self, pos, ax=ax)


def _get_function(funcStr):

    if isinstance(funcStr, types.FunctionType):
        f = funcStr
    elif '.' in funcStr:
        try:
            instr_name, method = funcStr.split('.')
            instr = Instrument.find_instrument(instr_name)
            f = getattr(instr, method)
        except Exception:
            f = get_function_from_module(funcStr)
    return f

def get_function_from_module(funcStr):
    """
    """
    split_idx = funcStr.rfind('.')
    module_name = funcStr[:split_idx]
    mod = import_module(module_name)
    f = getattr(mod, funcStr[(split_idx+1):])
    return f

