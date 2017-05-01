import qcodes.utils.validators as vals
import autodepgraph.node_functions.calibration_functions as cal_f
import autodepgraph.node_functions.check_functions as check_f
from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ManualParameter


class CalibrationNode(Instrument):

    def __init__(self, name, verbose=False):
        super().__init__(name)
        self.add_parameter('state', parameter_class=ManualParameter,
                           docstring='',
                           vals=vals.Enum('good', 'needs calibration',
                                          'bad', 'unknown', 'active'),
                           initial_value='unknown')
        self.add_parameter('dependencies',
                           docstring='a list of names of Calibration nodes',
                           initial_value=[],
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)
        self.add_parameter('check_functions',
                           docstring='Name of the function that corresponds '
                                     + 'to checking the node',
                           initial_value=[],
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)
        self.add_parameter('calibrate_functions',
                           docstring='Name of the function that calibrating '
                           + 'the node',
                           initial_value=[],
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)
        self._parenth_graph = None

    def __call__(self, verbose=False):
        return self.execute_node(verbose=verbose)

    def update_monitor(self):
        # calls the update_monitor function on the parent graph
        if self._parenth_graph is not None:
            pg = self.find_instrument(self._parenth_graph)
            pg.update_monitor()

    def execute_node(self, verbose=False):
        """
        Checks the state of the node and executes the logic to try and reach a
        'good' state.
        """
        if verbose:
            print("Node {} state is '{}'.".format(self.name, self.state()))

        if self.state() == 'good':
            # Nothing to do
            self.update_monitor()
            return self.state()
        # If state is not good, start by checking dependencies
        # -> try to find the first node in the graph that is 'good'
        self.state('active')
        if not self.check_dependencies(verbose=verbose):
            # At least one dependency is not satisfied.
            self.state('unknown')
            self.update_monitor()
            return self.state()

        # If dependencies are satisfied, check the node itself.
        result = self.check(verbose=verbose)
        # if result is 'good' no calibration is necessary
        # if result is 'bad', calibration is not possible
        if result == 'needs calibration':
            if self.calibrate(verbose=verbose):
                # calibration successful
                self.update_monitor()
                self.state('good')
            else:
                # calibration unsuccessful
                self.update_monitor()
                self.state('bad')

        return self.state()

    def check_dependencies(self, verbose=False):
        '''
        Executes all nodes listed as dependencies and returns True if and
        and only if all dependencies report 'good' state.
        '''
        if verbose:
            print('Checking dependencies of node {}.'.format(self.name))
        checksPassed = True
        for dep in self.dependencies():
            depNode = self.find_instrument(dep)
            if depNode(verbose=verbose) != 'good':
                checksPassed = False

        if verbose:
            print('All dependencies of node {} satisfied: {}'
                  .format(self.name, checksPassed))

        return checksPassed

    def calibrate(self, verbose=False):
        '''
        Executes all calibration functions of the node, updates and returns
        the node state.
        '''
        if verbose:
            print('Calibrating node {}.'.format(self.name))

        self.state('active')
        result = True
        for funcStr in self.calibrate_functions():
            f = getattr(cal_f, funcStr)
            # If any of the calibrations returns False, result will be False
            result = (f() and result)

        if verbose:
            print('Calibration of node {} successful: {}'
                  .format(self.name, result))

        if result is True:
            self.state('good')
            return True
        else:
            self.state('bad')
            return False

    def check(self, verbose=False):
        '''
        Runs checks of the node. The state is set according to the following
        logic:
            'good': all checks pass
            'needs calibration': at least one check finds that it needs
                calibration and no check fails
            'bad': at least one check fails
        '''
        if verbose:
            print('Checking node {}.'.format(self.name))

        self.state('active')
        needsCalib = False  # Set to True if a check finds 'needs calibration'
        broken = False  # Set to True if a check fails.
        for funcStr in self.check_functions():
            f = getattr(check_f, funcStr)
            result = f()
            if result == 'needs calibration':
                needsCalib = True
            if result == 'bad':
                broken = True

        if verbose:
            print('Needs {} calibration: {}'.format(self.name, needsCalib))
            print('Node {} broken: {}'.format(self.name, broken))

        if not needsCalib and not broken:
            self.state('good')
        elif needsCalib and not broken:
            self.state('needs calibration')
        elif broken:
            self.state('bad')

        return self.state()
