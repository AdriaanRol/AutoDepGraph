import qcodes.utils.validators as vals
import logging
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

        self.add_parameter('parents',
                           docstring='List of names of nodes '
                                     'on which this node depends. '
                                     'To add or remove nodes use the '
                                     'add_parent and remove_parent '
                                     'methods.',
                           get_cmd=self._get_parents,
                           vals=vals.Lists(vals.Strings()))
        self._parents = []
        self.add_parameter('children',
                           docstring='List of names of nodes '
                                     'which depend on this node. '
                                     'Not intended to be set directly. '
                                     'Children are automatically added '
                                     'whenever this node is added as a '
                                     'parent to another node.',
                           get_cmd=self._get_children,
                           vals=vals.Lists(vals.Strings()))
        self._children = []

        chk_docst = (
            'Name of the function used to perform the check, can be either a '
            'function in the check_functions module or a method of an '
            'instrument. If it is a method of an instrument it can be '
            'specified as "instr_name.method_name".\nA check function must '
            'return one of the possible states of a node, see also the state'
            'docstring.')

        self.add_parameter('check_functions',
                           docstring=chk_docst,
                           initial_value=[],
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)
        cal_docst = (
            'Name of the function used to calibrate a node, can be either a '
            'function in the calibrate_functions module or a method of an '
            'instrument. If it is a method of an instrument it can be '
            'specified as "instr_name.method_name".\nA calibrate function '
            'must return True or False indicating the success of the '
            'calibration.')
        self.add_parameter('calibrate_functions',
                           docstring=cal_docst,
                           initial_value=[],
                           vals=vals.Lists(vals.Strings()),
                           parameter_class=ManualParameter)

        # counters to count how often functions get called for debugging
        # purposes
        self._exec_cnt = 0
        self._calib_cnt = 0
        self._check_cnt = 0

    def __call__(self, verbose=False):
        return self.execute_node(verbose=verbose)

    def _set_state(self, val):
        self.state._latest_set_ts = datetime.now()
        self._state = val

    def _get_state(self):
        deltaT = (datetime.now() - self.state._latest_set_ts).total_seconds()
        if deltaT > self.calibration_timeout():
            self._state = 'needs calibration'
        return self._state

    def _get_parents(self):
        return self._parents

    def _get_children(self):
        return self._children

    def close(self):
        '''
        Removes reference to this node from its parents and close the
        instrument.
        Note: References to this node from child nodes are not removed
        because we want to know about it if removing this breaks a dependency.
        '''
        for node_name in self.parents():
            try:
                node = self.find_instrument(node_name)
                if self.name in node.children():
                    node.children().remove(self.name)
            except KeyError:
                # if the other node is not found, the reference does not need
                # to be removed anyway
                pass

        super().close()

    def add_parent(self, node):
        '''
        Adds a parent to this node. Also adds this node to the children of
        the new parent node.
        The argument node can be a string, or a node object, or a
        list/numpy.array of these types.
        '''
        if isinstance(node, list) or isinstance(node, np.ndarray):
            for i in node:
                self.add_parent(i)
        else:
            if isinstance(node, CalibrationNode):
                name = node.name
            else:
                name = node
                node = self.find_instrument(name)

            if name not in self.parents():
                self.parents().append(name)
            else:
                logging.warning('Node "{}" is already a parent of node "{}"'
                                .format(name, self.name))

            if self.name not in node.children():
                node.children().append(self.name)

    def remove_parent(self, node):
        '''
        Removes a parent node from this node. By default also removes this
        node from the child nodes of the removed parent.
        node can be a string or a node object.
        '''
        if isinstance(node, list) or isinstance(node, np.ndarray):
            for i in node:
                self.remove_parent(i)
        else:
            if isinstance(node, CalibrationNode):
                name = node.name
            else:
                name = node

            if name in self.parents():
                self.parents().remove(name)
            else:
                logging.warning('Could not remove parent "{}" from node "{}": '
                                .format(name, self.name)
                                + '"{}" not in self.parents()'.format(name))

            try:
                node = self.find_instrument(name)
                if self.name in node.children():
                    node.children().remove(self.name)
            except KeyError:
                logging.warning('Parent node "{}" not found.'.format(name))

    def propagate_error(self, state):
        '''
        Sets the state of this node to 'state' and calls this method for all
        child nodes (nodes that depend on this node). Used for recursively
        propagate errors.
        '''
        self.state(state)
        for child_name in self.children():
            # This will result in a depth-first search through the graph
            # that is quite inefficient and can visit many nodes multiple
            # times. We don't really care though, since the graph shouldn't
            # larger than ~100 nodes.
            self.find_instrument(child_name).propagate_error(state)

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
        for dep_name in self.parents():
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
            for dep_name in self.parents():
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
