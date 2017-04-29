from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ManualParameter
from qcodes.utils import validators as vals
"""
This contains the definition
"""


class graph():
    """
    A class containing nodes
    """

    def load_graph(self, filename):
        """
        Loads a graph.
        """
        raise NotImplementedError()

    def save_graph(self, filename):
        """
        Saves a text based representation of the current graph
        """
        raise NotImplementedError()

    def add_node(self, node):
        self.nodes.append(node)



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
