
from qcodes.instrument.base import Instrument
import yaml
import logging
from autodepgraph.node import CalibrationNode
import autodepgraph.visualization as vis
from os.path import join, split
import matplotlib.pyplot as plt
from qcodes.instrument.parameter import ManualParameter
from qcodes.utils.validators import Enum, Strings


try:
    # Serves as a test to see if pyqtgraph is available
    import pyqtgraph as pg
    plot_mode = 'pyqtgraph'
except ImportError:
    plot_mode = 'matplotlib'

try:
    import pygraphviz
except ImportError:
    logging.warning('pygraphviz is not installed, plotting will be disabled')
    plot_mode = 'None'


_path_name = split(__file__)[:-1][0]


class Graph(Instrument):
    """
    A class containing nodes
    """
    delegate_attr_dicts = ['nodes', 'parameters']

    def __init__(self, name):
        super().__init__(name)
        self.plot_mode = plot_mode
        self.nodes = {}
        self._graph_changed_since_plot = False
        self.add_parameter('cfg_plot_mode',
                           initial_value=plot_mode,
                           parameter_class=ManualParameter,
                           vals=Enum('html', 'pyqtgraph', 'matplotlib',
                                     'dotfile',
                                     'None'))

        self.add_parameter(
            'cfg_dot_filename',
            initial_value=join(_path_name,'svg_viewer', 'adg_graph.dot'),
            parameter_class=ManualParameter,
            vals=Strings())
        self.add_parameter(
            'cfg_svg_filename',
            initial_value=join(_path_name,'svg_viewer', 'adg_graph.svg'),
            parameter_class=ManualParameter,
            vals=Strings())

    def load_graph(self, filename, load_node_state=False):
        """
        Loads a graph.
        """
        graph_snap = yaml.safe_load(open(filename, 'r'))

        # First all nodes are added
        for node_snap in graph_snap['nodes'].values():
            try:
                # Look for an existing node
                node = self.find_instrument(node_snap['name'])
                # no parameters indicates closed instrument -> open a new one
                if not hasattr(node, 'parameters'):
                    node = CalibrationNode(node_snap['name'])
            except KeyError:
                # If the node does not exist, create a new node
                node = CalibrationNode(node_snap['name'])
            self.add_node(node)

        # ## Only after all nodes are added, the parameters are set. ##
        # it is important the nodes are created first as setting a parent
        # for a node requires it to exist so that children can be added.
        for node_snap in graph_snap['nodes'].values():
            node = self.nodes[node_snap['name']]
            # children is not in pars_to_update because the children are set
            # whenever a node is added as a parent to another node. This means
            # that loading and setting parents for all node automatically also
            # sets the children for all nodes correctly.
            pars_to_update = ['parents', 'check_function',
                              'calibrate_function', 'calibration_timeout']
            if load_node_state:
                pars_to_update += ['state']

            pars = node_snap['parameters']
            for parname in pars_to_update:
                val = pars[parname]['value']
                if val is not None:
                    node.set(parname, val)

    def save_graph(self, filename):
        """
        Saves a text based representation of the current graph
        """
        f = open(filename, 'w')
        yaml.dump(self.snapshot(), f)

    def snapshot(self, update=False):
        snap = {'nodes': {},
                'meta': {}}
        for node in self.nodes.values():
            snap['nodes'][node.name] = node.snapshot(update=update)
        return snap

    def add_node(self, node,  parents=None):
        """
        Adds a node to the graph.
        Args:
            node (instr/str) : the node to be added. Can be either by
                                name (str) or as a Node object (instrument)
        """
        if isinstance(node, str):
            try:  # look for an existing node instrument
                node = self.find_instrument(node)
            except KeyError:
                node = CalibrationNode(node)
        if node.name in self.nodes.keys():
            logging.warning(
                'Node "{}" already exists in graph'.format(node.name))
        # gives the node a reference to the parent graph
        node._parent_graph = self.name
        self.nodes[node.name] = node

        # Clears the node positions used for mpl plotting when a new node
        # is added
        self._node_pos = None
        self._graph_changed_since_plot = True

        if parents is not None:
            node.parents(parents)

        return node

    def clear_node_state(self):
        for node in self.nodes.values():
            node.state('unknown')

    def update_monitor(self):
        if self.cfg_plot_mode() == 'matplotlib':
            self.update_monitor_mpl()
        elif self.cfg_plot_mode() == 'pyqtgraph':
            self.update_monitor_pg()
        elif self.cfg_plot_mode() == 'html':
            self.update_monitor_html()
        elif self.cfg_plot_mode() == 'dotfile':
            self.write_to_dotfile()
        elif self.cfg_plot_mode() == 'None':
            return

    def write_to_dotfile(self, filename: str=None):
        if filename is None:
            filename = self.cfg_dot_filename()
        vis.draw_graph_svg(self.snapshot(), filename=filename)

    def update_monitor_html(self):
        """
        Generates an svg using networkx and pygraphviz. The file location
        is the default location used by the autodepgraph svg viewer
        """
        vis.draw_graph_svg(self.snapshot(), filename=self.cfg_svg_filename())

    def update_monitor_mpl(self):
        """
        Updates a plot using the draw_graph_mpl function from the
        visualization module.
        The current visualization is based on matplotlib.
        """
        plt.clf()
        for node in self.nodes.values():
            # ensures states are updated before taking snapshot
            node.state()
        self._node_pos = vis.draw_graph_mpl(
            self.snapshot(), pos=self._node_pos)
        plt.draw()
        plt.pause(.05)

    def update_monitor_pg(self):
        if not hasattr(self, 'DiGraphWindow'):
            self.DiGraphWindow = None
        for node in self.nodes.values():
            # ensures states are updated before taking snapshot
            node.state()
        if self._graph_changed_since_plot and self.DiGraphWindow is not None:
            self.DiGraphWindow.clear()
        self.DiGraphWindow = vis.draw_graph_pyqt(
            self.snapshot(), DiGraphWindow=self.DiGraphWindow,
            window_title=self.name)
        self._graph_changed_since_plot = False
