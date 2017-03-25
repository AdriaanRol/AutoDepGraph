from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ManualParameter
"""
This contains the definition
"""
class graph():
    """
    A class containing nodes
    """
    self.nodes = []



    def load_graph(self, filename):
        """
        Saves the current graph in a text based format
        """

    def save_graph(self, filename):
        """
        Saves a text based representation of the current graph
        """
    def add_node(self, node):
        self.nodes +=


class CalibrationNode(Instrument):
    def __init__(self, name):
        super().__init__(name)
        self.add_parameter(
            'state'
            parameter_class=ManualParameter,
            docstring='',
            vals=vals.Enum('good', 'needs calibration',
                           'bad', 'unknown', 'active'),
            initial_value='unknown')
        self.add_parameter('dependencies',
                           docstring='a list of names of Calibration nodes'=
                           vals=vals.Lists(vals.Strings()))

    def execute_node()
        """
        Contains the logic of the nodes will have
        """
        state = self.state()
        if state == 'good':
            return True
        if self.state == 'bad':
            self.check_dependencies()
        return self.calibrate()







    #     print('hello')

    # def check_state(self):
    #     return self.state
