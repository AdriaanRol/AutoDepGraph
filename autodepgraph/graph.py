
from qcodes.instrument.base import Instrument
import yaml
import logging
from autodepgraph.node import CalibrationNode


class Graph(Instrument):
    """
    A class containing nodes
    """
    delegate_attr_dicts = ['nodes']

    def __init__(self, name):
        super().__init__(name)
        self.nodes = {}

    def load_graph(self, filename, load_node_state=False):
        """
        Loads a graph.
        """
        graph_snap = yaml.safe_load(open(filename, 'r'))
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

            pars_to_update = ['dependencies', 'check_functions',
                              'calibrate_functions']
            if load_node_state:
                pars_to_update += ['state']

            pars = node_snap['parameters']
            for parname in pars_to_update:
                val = pars[parname]['value']
                if val is not None:
                    node.set(parname, val)
            self.add_node(node)

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

    def add_node(self, node):
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
            logging.warning('Node already exists in graph')
        self.nodes[node.name] = node
