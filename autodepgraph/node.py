import qcodes.utils.validators as vals
import autodepgraph.calibrate_functions as cal_f
import autodepgraph.check_functions as check_f
from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ManualParameter


class CalibrationNode(Instrument):
    def __init__(self, name, verbose=False):
        super().__init__(name)
        self._verbose = verbose
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
        Checks the state of the node and executes the logic to try and reach a
        'good' state.
        """
        if self._verbose:
            print("Node state is '{}'.".format(self.state()))

        if self.state() == 'good':
            # Nothing to do
            return self.state()

        # If state is not good, start by checking dependencies
        # -> try to find the first node in the graph that is 'good'
        if self.check_dependencies():
            self.check()
            self.calibrate()
        else:
            # At least one dependency is not satisfied.
            if self._verbose:
                print('Dependencies of node {} not satisfied.'
                      .format(self.name))
            self.state('unknown')

        return self.state()

    def check_dependencies(self):
        '''
        Executes all nodes listed as dependencies and returns True if and
        and only if all dependencies report 'good' state.
        '''
        if self._verbose:
            print('Checking dependencies of node {}.'.format(self.name))
        checksPassed = True
        for dep in self.dependencies():
            depNode = self.find_instrument(dep)
            if depNode() != 'good':
                checksPassed = False

        return checksPassed

    def calibrate(self):
        '''
        Executes all calibration functions of the node, updates and returns
        the node state.
        '''
        if self._verbose:
            print('Calibrating node {}.'.format(self.name))

        self.state('active')
        result = True
        for funcStr in self.calibrate_functions():
            f = getattr(cal_f, funcStr)
            # If any of the calibrations returns False, result will be False
            result = (f() and result)

        if result is True:
            self.state('good')
        else:
            self.state('bad')
        return self.state()

    def check(self):
        '''
        Runs checks of the node. The state is set according to the following
        logic:
            'good': all checks pass
            'needs calibration': at least one check finds that it needs
                calibration and no check fails
            'bad': at least one check fails
        '''
        if self._verbose:
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

        if not needsCalib and not broken:
            self.state('good')
        elif needsCalib and not broken:
            self.state('needs calibration')
        elif broken:
            self.state('bad')

        return self.state()
