import qcodes as qc
from autodepgraph.graph import CalibrationNode, Graph
from unittest import TestCase
from qcodes.instrument.base import Instrument


class Test_GraphLogic(TestCase):
    # Test graph:
    #     B <-- A
    #     |    /
    #     v   /
    #     C <-

    @classmethod
    def setUpClass(self):
        # Construct the nodes
        self.dummy_graph = Graph('dummy_graph')
        self.node_a = CalibrationNode('A')
        self.node_b = CalibrationNode('B')
        self.node_c = CalibrationNode('C')
        self.dummy_graph.add_node(self.node_a)
        self.dummy_graph.add_node(self.node_b)
        self.dummy_graph.add_node(self.node_c)

        # Link the nodes
        self.node_a.parents(['B', 'C'])
        self.node_b.parents(['C'])
        self.node_c.parents([])

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions()
        self.node_b.check_functions()
        self.node_c.check_functions()

        self.node_a.calibrate_functions()
        self.node_b.calibrate_functions()
        self.node_c.calibrate_functions()

    def test_all_good(self):
        # All checks and calibrations pass.
        print('\n')
        print("Testing case 'all good'.")
        self.node_a.state('unknown')
        self.node_b.state('unknown')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_good'])
        self.node_b.check_functions(['test_check_good'])
        self.node_c.check_functions(['test_check_good'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_True'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        # Execute node a. Nodes B and C should be asked for their state but
        # not executed
        self.node_a._exec_cnt = 0
        self.node_b._exec_cnt = 0
        self.node_c._exec_cnt = 0

        self.node_a._check_cnt = 0
        self.node_b._check_cnt = 0
        self.node_c._check_cnt = 0

        self.node_a._calib_cnt = 0
        self.node_b._calib_cnt = 0
        self.node_c._calib_cnt = 0

        self.node_a(verbose=True)
        self.assertEqual(self.node_a.state(), 'good')
        self.assertEqual(self.node_b.state(), 'unknown')
        self.assertEqual(self.node_c.state(), 'unknown')

        self.assertEqual(self.node_a._exec_cnt, 1)
        self.assertEqual(self.node_b._exec_cnt, 0)
        self.assertEqual(self.node_c._exec_cnt, 0)

        self.assertEqual(self.node_a._check_cnt, 1)
        self.assertEqual(self.node_b._check_cnt, 0)
        self.assertEqual(self.node_c._check_cnt, 0)

        self.assertEqual(self.node_a._calib_cnt, 0)
        self.assertEqual(self.node_b._calib_cnt, 0)
        self.assertEqual(self.node_c._calib_cnt, 0)

    def test_need_calib_check(self):
        # All nodes need calibration.
        print('\n')
        print("Testing case 'all need calibration'.")

        # Reset the node states
        self.node_a.state('unknown')
        self.node_b.state('needs calibration')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_needs_calibration'])
        self.node_b.check_functions(['test_check_needs_calibration'])
        self.node_c.check_functions(['test_check_needs_calibration'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_True'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        self.node_a._exec_cnt = 0
        self.node_b._exec_cnt = 0
        self.node_c._exec_cnt = 0

        self.node_a._check_cnt = 0
        self.node_b._check_cnt = 0
        self.node_c._check_cnt = 0

        self.node_a._calib_cnt = 0
        self.node_b._calib_cnt = 0
        self.node_c._calib_cnt = 0

        # Execute node a. since it depends on B and C and only B is not
        # in good/unknown only B will also be checked and calibrated
        self.node_a(verbose=True)
        self.assertEqual(self.node_a.state(), 'good')
        self.assertEqual(self.node_b.state(), 'good')
        self.assertEqual(self.node_c.state(), 'unknown')

        self.assertEqual(self.node_a._exec_cnt, 1)
        self.assertEqual(self.node_b._exec_cnt, 1)
        self.assertEqual(self.node_c._exec_cnt, 0)

        self.assertEqual(self.node_a._check_cnt, 1)
        # needs calibration will always skip the check and go to calibrating
        self.assertEqual(self.node_b._check_cnt, 0)
        self.assertEqual(self.node_c._check_cnt, 0)

        self.assertEqual(self.node_a._calib_cnt, 1)
        self.assertEqual(self.node_b._calib_cnt, 1)
        self.assertEqual(self.node_c._calib_cnt, 0)

    def test_check_A_bad(self):
        # Reset the node states
        self.node_a.state('unknown')
        self.node_b.state('unknown')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_bad'])
        self.node_b.check_functions(['test_check_needs_calibration'])
        self.node_c.check_functions(['test_check_good'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_True'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        # Execute node a. Since check returns bad, all nodes should be called
        self.node_a._exec_cnt = 0
        self.node_b._exec_cnt = 0
        self.node_c._exec_cnt = 0

        self.node_a._check_cnt = 0
        self.node_b._check_cnt = 0
        self.node_c._check_cnt = 0

        self.node_a._calib_cnt = 0
        self.node_b._calib_cnt = 0
        self.node_c._calib_cnt = 0
        self.node_a(verbose=True)

        # All calibration functions are set to "good"
        self.assertEqual(self.node_a.state(), 'good')
        self.assertEqual(self.node_b.state(), 'good')
        self.assertEqual(self.node_c.state(), 'good')

        self.assertEqual(self.node_a._exec_cnt, 1)
        self.assertEqual(self.node_b._exec_cnt, 1)
        self.assertEqual(self.node_c._exec_cnt, 1)

        self.assertEqual(self.node_a._check_cnt, 1)
        self.assertEqual(self.node_b._check_cnt, 1)
        self.assertEqual(self.node_c._check_cnt, 1)

        self.assertEqual(self.node_a._calib_cnt, 1)
        self.assertEqual(self.node_b._calib_cnt, 1)
        self.assertEqual(self.node_c._calib_cnt, 0)  # check returns good

    def test_B_calibration_bad(self):
        # All nodes need calibration.

        # Reset the node states
        self.node_a.state('unknown')
        self.node_b.state('unknown')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_bad'])
        self.node_b.check_functions(['test_check_needs_calibration'])
        self.node_c.check_functions(['test_check_good'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_False'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        self.node_a._exec_cnt = 0
        self.node_b._exec_cnt = 0
        self.node_c._exec_cnt = 0

        self.node_a._check_cnt = 0
        self.node_b._check_cnt = 0
        self.node_c._check_cnt = 0

        self.node_a._calib_cnt = 0
        self.node_b._calib_cnt = 0
        self.node_c._calib_cnt = 0

        # Execute node a. Since it depends on B and C, all checks and
        # calibrations should be called.
        with self.assertRaises(ValueError):
            self.node_a(verbose=True)

        # State set to bad when calibration fails
        self.assertEqual(self.node_a.state(), 'bad')
        self.assertEqual(self.node_b.state(), 'bad')
        self.assertEqual(self.node_c.state(), 'good')

        self.assertEqual(self.node_a._exec_cnt, 1)
        self.assertEqual(self.node_b._exec_cnt, 1)
        self.assertEqual(self.node_c._exec_cnt, 1)

        self.assertEqual(self.node_a._check_cnt, 1)
        self.assertEqual(self.node_b._check_cnt, 1)
        self.assertEqual(self.node_c._check_cnt, 1)

        # Cannot satisfy dependency so it will not calibrate
        self.assertEqual(self.node_a._calib_cnt, 0)
        # not testing the calib count of the others as the order of
        # dependencies is unordered

    def test_node_without_graph(self):
        node_d = CalibrationNode('D')
        with self.assertRaises(AttributeError):
            node_d()

    @classmethod
    def tearDownClass(self):
        # finds and closes all qcodes instruments
        all_instrs = (list(qc.Instrument._all_instruments.keys()))
        for insname in all_instrs:
            try:
                qc.Instrument.find_instrument(insname).close()
            except KeyError:
                pass


class Test_Node(TestCase):
    """
    Tests the logic of nodes that does not relate to other nodes or graphs.
    """

    def test_name(self):
        node_a = CalibrationNode('A')
        self.assertEqual(node_a.name, 'A')

    def test_timeout(self):
        node_b = CalibrationNode('B')
        node_b.state('good')
        node_b.calibration_timeout(1)
        state_before_timeout = node_b.state()
        self.assertEqual(state_before_timeout, 'good')
        import time
        time.sleep(1)
        node_b.calibration_timeout(0)
        state_after_timeout = node_b.state()
        print(state_after_timeout)

        self.assertEqual(state_after_timeout, 'needs calibration')

    def test_instrument_method_as_calibfunc(self):
        node_c = CalibrationNode('C')
        mock_instr = MockInstrument('mock_instr')

        node_c.calibrate_functions(['mock_instr.calibrate'])
        node_c.check_functions(['mock_instr.check_state'])

        self.assertEqual(mock_instr.check_cnt, 0)
        node_c.check()
        self.assertEqual(mock_instr.check_cnt, 1)

        self.assertEqual(mock_instr.cal_cnt, 0)
        node_c.calibrate()
        self.assertEqual(mock_instr.cal_cnt, 1)

    @classmethod
    def tearDownClass(self):
        # finds and closes all qcodes instruments
        all_instrs = (list(qc.Instrument._all_instruments.keys()))
        for insname in all_instrs:
            try:
                qc.Instrument.find_instrument(insname).close()
            except KeyError:
                pass


class MockInstrument(Instrument):
    '''
    '''

    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        self.check_cnt = 0
        self.cal_cnt = 0

    def check_state(self):
        self.check_cnt += 1
        return 'good'

    def calibrate(self):
        self.cal_cnt += 1
        return True
