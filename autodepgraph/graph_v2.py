import numpy as np
import types
import networkx as nx
import matplotlib.pyplot as plt
from autodepgraph.visualization import state_cmap


# Used to find functions in modules
from importlib import import_module
# Only used for finding instrument methods.
from qcodes.instrument.base import Instrument


class AutoDepGraph_DAG(nx.DiGraph):
    def __init__(self, name, cfg_plot_mode=None,
                 incoming_graph_data=None, **attr):
        """
        Directed Acyclic Graph used for calibrations.
        Inherits from a networkx DiGraph.

        The AutoDepGraph provides several constraints to nodes and edges
        as well as add the functionality to walk over the graph and visualize this.
        """
        attr['name'] = name
        self.cfg_plot_mode = cfg_plot_mode

        super().__init__(incoming_graph_data, **attr)

        # counters to count how often functions get called for debugging
        # purposes
        self._exec_cnt = 0
        self._calib_cnt = 0
        self._check_cnt = 0

    def add_node(self, node_for_adding, **attr):
        """
        """
        # there are set here to ensure these node attributes exist.
        # setting in this way will most likely interfere with joining multiple graphs
        attr['state'] = attr.get('state', 'unknown')
        attr['timeout'] = attr.get('timeout',
                                               np.inf)
        attr['calibrate_function'] = attr.get('calibrate_function',
            'autodepgraph.node_functions.calibration_functions'+
            '.NotImplementedCalibration')

        attr['check_function']= attr.get('check_function',
            'autodepgraph.node_functions.check_functions'+
            '.return_fixed_value')

        # zero default tolerance -> always recalibrate
        attr['tolerance']= attr.get('tolerance', 0)
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
        """
        Executing a node attempts to go from any state to a good state.
            any_state -> good

        Executing a node performs the following steps:
            1. get the state of the dependency nodes. If all are OK or unknown,
               perform a check on the node itself.
               If a node is any other state, execute it to move it to a
               good state
            2. perform the "check" experiment on the node itself. This quick
               check
            3. Perform calibration and second round of executing dependencies
        """
        self._exec_cnt += 1
        if verbose:
            print('Executing node "{}".'.format(node))

        # 1. Going over the states of all the required nodes and ensure
        # these are all in a 'Good' state.
        for req_node_name in self.adj[node]:
            req_node_state = self.nodes[req_node_name]['state']
            if req_node_state in ['good', 'unknown']:
                continue  # assume req_node is in a good state
            else: # executing the node to ensure it is in a good state
                req_node_state = self.execute_node(req_node_name,
                                                   verbose=verbose)
                if req_node_state == 'bad':
                    raise ValueError('Could not calibrate "{}"'.format(
                        req_node_name))

        # 2. Once all required nodes are OK, determine action to be taken
        state = self.nodes[node]['state']
        if state == 'needs calibration':
            # action is clear, no check required
            pass
        else:
            # determine latest status of node
            state = self.check_node(node, verbose=verbose)
        self.update_monitor()

        # 3. Take action based on the stae of the node
        if state == 'needs calibration':
            cal_succes = self.calibrate_node(node, verbose=verbose)
            # the calibration can still fail if dependencies that were good
            # or unknown were bad. In that case all dependencies will
            # explicitly be executed and calibration will be retried
            if not cal_succes:
                state = 'bad'
                if verbose:
                    print('Initial calibration of "{}" failed, '
                          'retrying.'.format(node))
        if state == 'bad':
            # if the state is bad it will execute *all* dependencies. Even
            # the ones that were updated before.
            if verbose:
                print('State of node "{}" is bad, executing all required'
                      ' nodes.'.format(node))
            for req_node_name in self.adj[node]:
                req_node_state = self.execute_node(req_node_name,
                                                   verbose=verbose)
            cal_succes = self.calibrate_node(node, verbose=verbose)
            if not cal_succes:
                raise ValueError(
                    'Calibration of "{}" failed.'.format(node))

        state = self.nodes[node]['state']
        return state


    def check_node(self, node, verbose=False):
        if verbose:
            print('\tChecking node {}.'.format(node))
        self.nodes[node]['state'] = 'active'
        self.update_monitor()
        func = _get_function(self.nodes[node]['check_function'])
        result = func()
        if isinstance(result, float):
            if result <self.nodes[node]['tolerance']:
                self.nodes[node]['state'] = 'good'
                if verbose:
                    print('\tNode {} is within tolerance.'.format(node))
            else:
                self.nodes[node]['state'] = 'needs calibration'
                if verbose:
                    print('\tNode {} needs calibration.'.format(node))
        elif result == False:
            if verbose:
                print('\tNode {} is in a "bad" state.'.format(node))
            # if the function returns False it means the check is broken
            self.nodes[node]['state'] = 'bad'
        else:
            raise ValueError('Expected float or "False", '
                             'result is: {}'.format(result))

        return self.nodes[node]['state']


    def calibrate_node(self, node, verbose=False):
        if verbose:
            print('\tCalibrating node {}.'.format(node))
        self.nodes[node]['state'] = 'active'
        self.update_monitor()
        func = _get_function(self.nodes[node]['calibrate_function'])
        result = func()
        if result:
            self.nodes[node]['state'] = 'good'
            if verbose:
                print('\tCalibration of node {} successful.'.format(node))
        else:
            self.nodes[node]['state'] = 'bad'
            if verbose:
                print('\tCalibration of node {} failed.'.format(node))
        self.update_monitor()
        return self.nodes[node]['state']

    def set_all_node_states(self, state):
        for node_dat in self.nodes.values():
            node_dat['state'] = state

    def update_monitor(self):
        if self.cfg_plot_mode == 'matplotlib':
            self.update_monitor_mpl()
        elif self.cfg_plot_mode == 'pyqtgraph':
            self.update_monitor_pg()
        elif self.cfg_plot_mode == 'html':
            self.update_monitor_html()
        elif self.cfg_plot_mode == 'dotfile':
            self.write_to_dotfile()
        elif self.cfg_plot_mode == 'None':
            return

    def update_monitor_mpl(self):
        """
        Updates a plot using the draw_graph_mpl based on matplotlib.
        """
        plt.clf()
        self.draw_mpl()
        plt.draw()
        plt.pause(.05)

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

