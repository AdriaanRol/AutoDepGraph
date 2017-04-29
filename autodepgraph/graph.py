
from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ManualParameter
from qcodes.utils import validators as vals
import yaml
import logging


class Graph(Instrument):
    """
    A class containing nodes
    """

    def __init__(self, name):
        super().__init__(name)
        self._nodes = {}

    def load_graph(self, filename, load_node_state=False):
        """
        Loads a graph.
        """
        graph_snap = yaml.safe_load(open(filename, 'r'))
        for key, node_snap in graph_snap['nodes'].items():
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
        for nodename, node in self._nodes.items():
            snap['nodes'][node.name] = node.snapshot(update=update)
        return snap

    def add_node(self, node):
        if node.name in self._nodes.keys():
            logging.warning('Node already exists in graph')
        self._nodes[node.name] = node


class CalibrationNode(Instrument):

    def __init__(self, name):
        super().__init__(name)
        self.add_parameter('state', parameter_class=ManualParameter,
                           docstring='',
                           vals=vals.Enum('good', 'needs calibration',
                                          'bad', 'unknown', 'active'),
                           initial_value='unknown')

        self.add_parameter('dependencies',
                           docstring='a list of names of Calibration nodes',
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)
        self.add_parameter('check_functions',
                           docstring='Name of the function that corresponds to checking the node',
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)
        self.add_parameter('calibrate_functions',
                           docstring='Name of the function that calibrating the node',
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)

    def __call__(self):
        self.execute_node()

    def execute_node(self):
        """
        Contains the logic of the nodes will have
        """
        state = self.state()
        if state == 'good':
            print('Node is good')
            return True
        if self.state == 'bad':
            self.check_dependencies()
        self.calibrate()
        return self.state()

    def check_dependencies(self):
        return True

    def calibrate(self):
        print('calibrating '+self.name)
        self.state('good')  # set the state to good
        return True

    def check(self):
        self.state('needs calibration')
        return self.state()
