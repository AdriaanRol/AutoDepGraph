from autodepgraph.node import CalibrationNode
from unittest import TestCase
from copy import deepcopy


class Test_GraphLogic(TestCase):
    # Test graph:
    #     B <-- A
    #     |    /
    #     v   /
    #     C <-

    @classmethod
    def setUpClass(self):
        # Construct the nodes
        self.node_a = CalibrationNode('A')
        self.node_b = CalibrationNode('B')
        self.node_c = CalibrationNode('C')

        # Link the nodes
        self.node_a.dependencies(['B', 'C'])
        self.node_b.dependencies(['C'])
        self.node_c.dependencies([])

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions()
        self.node_b.check_functions()
        self.node_c.check_functions()

        self.node_a.calibrate_functions()
        self.node_b.calibrate_functions()
        self.node_c.calibrate_functions()

    def test_name(self):
        self.assertEqual(self.node_a.name, 'A')
        self.assertEqual(self.node_b.name, 'B')
        self.assertEqual(self.node_c.name, 'C')

    def test_all_good(self):
        # All checks and calibrations pass.
        print('\n')
        print("Testing case 'all good'.")

        # Reset the node states
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

        # Execute node a. Since it depends on B and C, all checks and
        # calibrations should be called.
        self.node_a(verbose=True)

        self.assertEqual(self.node_a.state(), 'good')
        self.assertEqual(self.node_b.state(), 'good')
        self.assertEqual(self.node_c.state(), 'good')

    def test_all_need_calib(self):
        # All nodes need calibration.

        print('\n')
        print("Testing case 'all need calibration'.")

        # Reset the node states
        self.node_a.state('unknown')
        self.node_b.state('unknown')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_needs_calibration'])
        self.node_b.check_functions(['test_check_needs_calibration'])
        self.node_c.check_functions(['test_check_needs_calibration'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_True'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        # Execute node a. Since it depends on B and C, all checks and
        # calibrations should be called.
        self.node_a(verbose=True)

        self.assertEqual(self.node_a.state(), 'good')
        self.assertEqual(self.node_b.state(), 'good')
        self.assertEqual(self.node_c.state(), 'good')

    def test_B_check_bad(self):
        # All nodes need calibration.
        print('\n')
        print("Testing case 'B check bad'.")

        # Reset the node states
        self.node_a.state('unknown')
        self.node_b.state('unknown')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_needs_calibration'])
        self.node_b.check_functions(['test_check_bad'])
        self.node_c.check_functions(['test_check_good'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_True'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        # Execute node a. Since it depends on B and C, all checks and
        # calibrations should be called.
        self.node_a(verbose=True)

        self.assertEqual(self.node_a.state(), 'unknown')
        self.assertEqual(self.node_b.state(), 'bad')
        self.assertEqual(self.node_c.state(), 'good')

    def test_B_calibration_bad(self):
        # All nodes need calibration.

        print('\n')
        print("Testing case 'B calibration bad'.")

        # Reset the node states
        self.node_a.state('unknown')
        self.node_b.state('unknown')
        self.node_c.state('unknown')

        # Populate nodes with checks and calibration functions
        self.node_a.check_functions(['test_check_needs_calibration'])
        self.node_b.check_functions(['test_check_needs_calibration'])
        self.node_c.check_functions(['test_check_good'])

        self.node_a.calibrate_functions(['test_calibration_True'])
        self.node_b.calibrate_functions(['test_calibration_False'])
        self.node_c.calibrate_functions(['test_calibration_True'])

        # Execute node a. Since it depends on B and C, all checks and
        # calibrations should be called.
        self.node_a(verbose=True)

        self.assertEqual(self.node_a.state(), 'unknown')
        self.assertEqual(self.node_b.state(), 'bad')
        self.assertEqual(self.node_c.state(), 'good')


        @classmethod
        def tearDownClass(self):
            # finds and closes all qcodes instruments
            all_instrs = deepcopy(list(self.node_a._all_instruments.keys()))
            for insname in all_instrs:
                try:
                    self.node_A.find_instrument(insname).close()
                except KeyError:
                    pass

