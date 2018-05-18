import logging
import numpy as np
import types
from datetime import datetime
import matplotlib.pyplot as plt
from os.path import join, split
import os
import tempfile
import webbrowser
import warnings

import networkx as nx
import autodepgraph
from autodepgraph.visualization import state_cmap
from autodepgraph import visualization as vis

# Used to find functions in modules
from importlib import import_module
# Only used for finding instrument methods.
from qcodes.instrument.base import Instrument


class AutoDepGraph_DAG(nx.DiGraph):

    node_states = ['good', 'needs calibration',
                         'bad', 'unknown', 'active']

    def __init__(self, name, cfg_plot_mode='svg',
                 incoming_graph_data=None, **attr):
        """
        Directed Acyclic Graph used for calibrations.
        Inherits from a networkx DiGraph.

        The AutoDepGraph provides several constraints to nodes and edges
        as well as add the functionality to walk over the graph in order to
        calibrate a node and visualize the graph in real-time.
        """
        attr['name'] = name
        self.cfg_plot_mode = cfg_plot_mode
        self.cfg_plot_mode_args = {'fig': None}

        _path_name = split(__file__)[:-1][0]
        self.cfg_svg_filename = join(_path_name, 'svg_viewer', 'adg_graph.svg')

        super().__init__(incoming_graph_data, **attr)

        # internal attributes
        self._DiGraphWindow = None  # used for pyqtgraph plotting
        self._graph_changed_since_plot = True  # used for pyqtgraph plotting

        # counters to count how often functions get called for debugging
        # purposes
        self._exec_cnt = 0
        self._calib_cnt = 0
        self._check_cnt = 0

    def fresh_copy(self):
        return AutoDepGraph_DAG(name=self.name,
                                cfg_plot_mode=self.cfg_plot_mode)

    def add_node(self, node_for_adding, **attr):
        """
        """
        # there are set here to ensure these node attributes exist.
        # setting in this way will most likely interfere
        # with joining multiple graphs
        attr['timeout'] = attr.get('timeout',
                                   np.inf)
        attr['calibrate_function'] = attr.get(
            'calibrate_function',
            'autodepgraph.node_functions.calibration_functions' +
            '.NotImplementedCalibration')

        attr['check_function'] = attr.get(
            'check_function',
            'autodepgraph.node_functions.check_functions' +
            '.return_fixed_value')

        # zero default tolerance -> always recalibrate
        attr['tolerance'] = attr.get('tolerance', 0)
        super().add_node(node_for_adding, **attr)

        self.set_node_state(node_for_adding,
                            state=attr.get('state', 'unknown'))
        # this adds a helper method to the attributes for quick access
        self._construct_maintenance_methods(nodes=[node_for_adding])

    def _construct_maintenance_methods(self, nodes):
        for n in nodes:
            self._construct_maintenance_method(node_name=n)

    def _construct_maintenance_method(self, node_name):
            node_name_no_space = node_name.replace(' ', '_').replace('-', '_')

            # This name exists so that text based storing falls back
            # on the right placeholder function
            def _construct_maintenance_method():
                self.maintain_node(node_name)

            self.__setattr__('maintain_{}'.format(node_name_no_space),
                             _construct_maintenance_method)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """
        Adds an edge that denotes a dependency in the calibration graph.
        u_of_edge -> v_of_edge denotes that u depends on v.
        """

        # Nodes must already exist to ensure they have the right properties
        if u_of_edge not in self.nodes():
            raise KeyError('{} not in nodes'.format(u_of_edge))
        if v_of_edge not in self.nodes():
            raise KeyError('{} not in nodes'.format(v_of_edge))
        super().add_edge(u_of_edge, v_of_edge, **attr)

    def get_node_state(self, node_name):
        Delta_T = (datetime.now() -
                   self.nodes[node_name]['last_update']).total_seconds()
        if (Delta_T > self.nodes[node_name]['timeout']):
            self.nodes[node_name]['state'] = 'unknown'
        return self.nodes[node_name]['state']

    def set_node_state(self, node_name, state, update_monitor=True):
        assert state in self.node_states
        self.nodes[node_name]['state'] = state
        self.nodes[node_name]['last_update'] = datetime.now()
        if update_monitor:
            self.update_monitor()

    def is_manual_node(self, node_name):
        if isinstance(self.nodes[node_name]['calibrate_function'], (types.MethodType, types.FunctionType)):
            return False
        elif 'manual' in self.nodes[node_name]['calibrate_function']:
            return True
        elif 'NotImplemented' in self.nodes[node_name]['calibrate_function']:
            return True
        else:
            return False

    def maintain_node(self, node, verbose=True):
        """
        Maintaining a node attempts to go from any state to a good state.
            any_state -> good

        Maintain a node performs the following steps:
            1. get the state of the dependency nodes. If all are OK or unknown,
               perform a check on the node itself.
               If a node is any other state, execute it to move it to a
               good state
            2. perform the "check" experiment on the node itself. This quick
               check
            3. Perform calibration and second round of maintaining dependencies
        """
        self._exec_cnt += 1
        if verbose:
            print('Maintaining node "{}".'.format(node))

        # 1. Going over the states of all the required nodes and ensure
        # these are all in a 'Good' state.
        for req_node_name in self.adj[node]:
            req_node_state = self.nodes[req_node_name]['state']
            if req_node_state in ['good', 'unknown']:
                continue  # assume req_node is in a good state
            else:  # maintaining the node to ensure it is in a good state
                req_node_state = self.maintain_node(req_node_name,
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
                print('State of node "{}" is bad, maintaining all required'
                      ' nodes.'.format(node))
            for req_node_name in self.adj[node]:
                req_node_state = self.maintain_node(req_node_name,
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
        self.set_node_state(node, 'active')

        func = _get_function(self.nodes[node]['check_function'])
        result = func()
        if isinstance(result, float):
            if result < self.nodes[node]['tolerance']:
                self.set_node_state(node, 'good')
                if verbose:
                    print('\tNode {} is within tolerance.'.format(node))
            else:
                self.set_node_state(node, 'needs calibration')
                if verbose:
                    print('\tNode {} needs calibration.'.format(node))

        elif result == False:
            if verbose:
                print('\tNode {} is in a "bad" state.'.format(node))
            # if the function returns False it means the check is broken
            self.set_node_state(node, 'bad')
        else:
            raise ValueError('Expected float or "False", '
                             'result is: {}'.format(result))

        return self.nodes[node]['state']

    def calibrate_node(self, node, verbose=False):
        if verbose:
            print('\tCalibrating node {}.'.format(node))
        self.set_node_state(node, 'active')

        func = _get_function(self.nodes[node]['calibrate_function'])
        try:
            result = func()
        except Exception as e:
            self.set_node_state(node, 'bad')
            logging.warning(e)
            return False
        if result:
            self.set_node_state(node, 'good')
            if verbose:
                print('\tCalibration of node {} successful.'.format(node))

            return True
        else:
            self.set_node_state(node, 'bad')
            if verbose:
                print('\tCalibration of node {} failed.'.format(node))

            return False

    def set_all_node_states(self, state):
        for node_dat in self.nodes.values():
            node_dat['state'] = state

    def update_monitor(self):
        if self.cfg_plot_mode == 'matplotlib':
            self.update_monitor_mpl()
        elif self.cfg_plot_mode == 'pyqtgraph':
            self.draw_pg()
        elif self.cfg_plot_mode == 'svg':
            self.draw_svg()
        elif self.cfg_plot_mode is None or self.cfg_plot_mode == 'None':
            return
        else:
            raise ValueError('cfg_plot_mode should be in ["matplotlib",'
                             ' "pyqtgraph", "svg", "None" ]')

    def update_monitor_mpl(self):
        """
        Updates a plot using the draw_graph_mpl based on matplotlib.
        """
        fig = self.cfg_plot_mode_args.get('fig', None)
        if fig is not None:
            plt.figure(fig)
        plt.clf()
        self.draw_mpl(plt.gca())
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

    def draw_pg(self, DiGraphWindow=None):
        """
        draws the graph using an interactive pyqtgraph window
        """
        if DiGraphWindow is None:
            DiGraphWindow = self._DiGraphWindow
        self._DiGraphWindow = vis.draw_graph_pyqt(
            self, DiGraphWindow=DiGraphWindow,
            window_title=self.name)
        return self._DiGraphWindow

    def draw_svg(self, filename: str=None):
        """
        """
        if filename is None:
            filename = self.cfg_svg_filename
        self._update_drawing_attrs()
        vis.draw_graph_svg(self, filename)

    def open_html_viewer(self):
        """ Open html viewer for the file specified by the svg backend """
        template = os.path.join(os.path.split(autodepgraph.__file__)[0], 'svg_viewer', 'svg_graph_viewer.html')
        with open(template, 'rt') as fid:
            x=fid.read()

        base, file = os.path.split(self.cfg_svg_filename)
        x=x.replace('adg_graph.svg', file)

        tfile=tempfile.mktemp(prefix='svgviewer-', suffix='html', dir=base)
        with open(tfile, 'wt') as fid:
            fid.write(x)
        webbrowser.open_new_tab(tfile)
        return tfile

    def set_node_attribute(self, node, attribute, value):
        """ Set the attribute of the specified node

        Args:
            node (str): name of the node
            attribute (str): attribute to set
            value (ojbect): value to set
        """
        if attribute in ['state']:
            raise Exception('please use set_state directly')
        nx.set_node_attributes(self, {node: {attribute: value}})

    def get_node_attribute(self, node, attribute):
        """ Return the attribute of the specified node

        Args:
            node (str): name of the node
            attribute (str): attribute to get
        Returns:
            value (ojbect): attribute of the object
        """
        if attribute in ['state']:
            raise Exception('please use get_state directly')
        return self.node[node][attribute]

    def set_node_description(self, node, description):
        """ Set the node description field

        Args:
            node (str): name of the node
            description (str): description to set
        """
        nx.set_node_attributes(self, {node: {'description': description}})

    def calibration_state(self):
        """ Return dictionary with current calibration state """
        return dict(self.node)

    def _update_drawing_attrs(self):
        for node_name, node_attrs in self.nodes(True):

            state = self.get_node_state(node_name)
            color = vis.state_cmap[state]
            shape = 'hexagon' if self.is_manual_node(node_name) else 'ellipse'
            attr_dict = {'shape': shape,
                         'style': 'filled',
                         'color': color,
                         # 'fixedsize':'shape',
                         # 'fixedsize' : b"true",
                         'fixedsize': "false",
                         'fillcolor': color}
            node_attrs.update(attr_dict)


def _construct_maintenance_method():
    # This placeholder exists to allow reading and writing graphs in a graph
    # based format.
    print('Placeholder function.')
    print('Call DAG._construct_maintenance_methods() to update methods.')


def _get_function(funcStr):

    if isinstance(funcStr, (types.MethodType, types.FunctionType)):
        warnings.warn('please set function as a str', DeprecationWarning)
        f = funcStr
    elif '.' in funcStr:
        try:
            instr_name, method = funcStr.split('.')
            instr = Instrument.find_instrument(instr_name)
            f = getattr(instr, method)
        except Exception as e:
            f = get_function_from_module(funcStr)
    else:
        raise Exception('could not find function %s' % funcStr)
    return f


def get_function_from_module(funcStr):
    """
    """
    split_idx = funcStr.rfind('.')
    module_name = funcStr[:split_idx]
    mod = import_module(module_name)
    f = getattr(mod, funcStr[(split_idx+1):])
    return f


def update_node_state(graph_to_update, graph_to_update_from):
    for node_name, attrs in graph_to_update_from.nodes(True):
        if node_name in graph_to_update.nodes():
            graph_to_update.nodes[node_name]['state'] = attrs['state']
            graph_to_update.nodes[node_name]['last_update'] = attrs['last_update']
