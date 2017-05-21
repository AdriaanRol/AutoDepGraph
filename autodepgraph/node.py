import qcodes.utils.validators as vals
import numpy as np
from datetime import datetime
import autodepgraph.node_functions.calibration_functions as cal_f
import autodepgraph.node_functions.check_functions as check_f
from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ManualParameter


class CalibrationNode(Instrument):

    def __init__(self, name, verbose=False):
        super().__init__(name)
        self.add_parameter(
            'state',
            docstring=('Returns the last known state of a node, if the state '
                       'is older than the "calibration_timeout" it will'
                       ' return needs calibration.'),
            get_cmd=self._get_state, set_cmd=self._set_state,
            vals=vals.Enum('good', 'needs calibration',
                           'bad', 'unknown', 'active'))
        self.state('unknown')  # sets the initial value

        self.add_parameter('calibration_timeout', unit='s',
                           docstring='',
                           initial_value=np.inf,
                           parameter_class=ManualParameter,
                           vals=vals.Numbers(min_value=0))

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

        # counters to count how often functions get called for debugging
        # purposes
        self._exec_cnt = 0
        self._calib_cnt = 0
        self._check_cnt = 0

    def _set_state(self, val):
        self.state._latest_set_ts = datetime.now()
        self._state = val

    def _get_state(self):
        deltaT = (datetime.now() - self.state._latest_set_ts).total_seconds()
        if deltaT > self.calibration_timeout():
            self._state = 'needs calibration'
        return self._state

    def __call__(self, verbose=False):
        return self.execute_node(verbose=verbose)

    def execute_node(self, verbose=False):
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
        if not hasattr(self, '_parenth_graph'):
            raise AttributeError(
                'Node "{}" must be attached to a graph'.format(self.name))
        if verbose:
            print('Executing node "{}".'.format(self.name))

        # 1. Going over the states of the dependencies
        # get the last known states of all dependencies
        dep_states = []
        for dep_name in self.dependencies():
            dep_state = self.find_instrument(dep_name).state()
            dep_states += [dep_state]
            if dep_state in ['good', 'unknown']:
                continue  # to self.check()
            else:
                # executing a node should change the state to good
                dep_state = self.find_instrument(dep_name).execute_node(
                    verbose=verbose)
                if dep_state == 'bad':
                    raise ValueError('Could not calibrate "{}"'.format(
                        dep_name))

        # 2. Determine action to be taken
        if self.state() != 'needs calibration':
            # skip the check if it is already known that calibration is needed
            state = self.check(verbose=verbose)
        else:
            state = self.state()
        self.update_graph_monitor()

        # 3. calibrate the node and it's requirements
        if state == 'needs calibration':
            cal_succes = self.calibrate(verbose=verbose)
            # the calibration can still fail if dependencies that were good
            # or unknown were bad. In that case all dependencies will
            # explicitly be executed and calibration will be retried
            if not cal_succes:
                state = 'bad'

        if state == 'bad':
            # if the state is bad it will execute *all* dependencies. Even
            # the ones that were updated before.
            for dep_name in self.dependencies():
                dep = self.find_instrument(dep_name)
                dep.execute_node(verbose=verbose)
            self.calibrate()
            if self.state() != 'good':
                raise ValueError(
                    'Calibration of "{}" failed.'.format(self.name))

        self.update_graph_monitor()
        return self.state()

    def calibrate(self, verbose=False):
        '''
        Performs the calibrations of a node, ideally moving the state to good
            needs calibration -> good

        Executes all calibration functions of the node, updates and returns
        the node state.
        '''
        self._calib_cnt += 1
        if verbose:
            print('\tCalibrating node {}.'.format(self.name))

        self.state('active')
        self.update_graph_monitor()
        result = True
        for funcStr in self.calibrate_functions():
            if '.' in funcStr:
                instr_name, method = funcStr.split('.')
                instr = self.find_instrument(instr_name)
                f = getattr(instr, method)
            else:
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
        self._check_cnt += 1
        if verbose:
            print('\tChecking node {}.'.format(self.name))

        self.state('active')
        self.update_graph_monitor()
        needsCalib = False  # Set to True if a check finds 'needs calibration'
        broken = False  # Set to True if a check fails.
        for funcStr in self.check_functions():
            if '.' in funcStr:
                instr_name, method = funcStr.split('.')
                instr = self.find_instrument(instr_name)
                f = getattr(instr, method)
            else:
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

    def update_graph_monitor(self):
        """
        if the node is part of a graph it will update the monitor using
        the update_monitor method of the parenth_graph
        """
        if hasattr(self, '_parenth_graph'):
            self.find_instrument(self._parenth_graph).update_monitor()
