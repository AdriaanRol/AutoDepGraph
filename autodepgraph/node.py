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

    def __call__(self, verbose=False):
        return self.execute_node(verbose=verbose)

    def execute_node(self, verbose=False):
        """
        Executing a node performs the following steps:
            - check the state of the node, if good and valid, return the
                state without performing any additional actions
            - if the state is anything else, start by checking dependencies
                after that the check experiment is performed

            - if calibration is needed run calibrations then update state and
                return true
            - if broken, execute dependencies, then recheck status and
                calibrate if needed. If check still returns broken. Abort.
        """
        if not hasattr(self, '_parenth_graph'):
            raise AttributeError(
                'Node "{}" must be attached to a graph'.format(self.name))

        if verbose:
            print('Executing node "{}".'.format(self.name))

        # Corresponds to a known good state.
        # An optional calibration valid time could be added to nodes.
        if self.state() == 'good':
            # Nothing to do
            self.find_instrument(self._parenth_graph).update_monitor()
            return self.state()

        # If state is not good, start by checking dependencies
        # -> try to find the first node in the graph that is 'good'
        self.state('active')
        if not self.check_dependencies(verbose=verbose):
            self.state('bad')
            raise ValueError(
                    'Could not satisfy dependencies of {}'.format(self.name))

        # If dependencies are satisfied, check the node itself.
        state = self.check(verbose=verbose)
        self.find_instrument(self._parenth_graph).update_monitor()

        if state == 'needs calibration':
            self.calibrate(verbose=verbose)
        elif state == 'bad':
            if self.check_dependencies(verbose=verbose):
                # Force a new check on all dependencies
                for dep_name in self.dependencies():
                    dep = self.find_instrument(dep_name)
                    dep.state('unknown')
                self.calibrate(verbose=verbose)
            else:
                self.state('bad')
                raise ValueError(
                    'Could not satisfy dependencies of {}'.format(self.name))
        self.find_instrument(self._parenth_graph).update_monitor()
        return self.state()

    def check_dependencies(self, verbose=False):
        '''
        Executes all nodes listed as dependencies and returns True if and
        and only if all dependencies report 'good' state.
        '''
        if verbose:
            print('\tChecking dependencies of node {}.'.format(self.name))
        checksPassed = True
        for dep in self.dependencies():
            depNode = self.find_instrument(dep)
            if depNode(verbose=verbose) != 'good':
                checksPassed = False

        if verbose:
            print('\tAll dependencies of node {} satisfied: {}'
                  .format(self.name, checksPassed))

        return checksPassed

    def calibrate(self, verbose=False):
        '''
        Executes all calibration functions of the node, updates and returns
        the node state.
        '''
        if verbose:
            print('\tCalibrating node {}.'.format(self.name))

        self.state('active')
        result = True
        for funcStr in self.calibrate_functions():
            f = getattr(cal_f, funcStr)
            # If any of the calibrations returns False, result will be False
            result = (f() and result)

        if verbose:
            print('\tCalibration of node {} successful: {}'
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
            print('\tChecking node {}.'.format(self.name))

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
            print('\tNeeds {} calibration: {}'.format(self.name, needsCalib))
            print('\tNode {} broken: {}'.format(self.name, broken))

        if not needsCalib and not broken:
            self.state('good')
        elif needsCalib and not broken:
            self.state('needs calibration')
        elif broken:
            self.state('bad')

        return self.state()
