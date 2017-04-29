from autodepgraph.graph import CalibrationNode

from unittest import TestCase


class Test_Node(TestCase):
    @classmethod
    def setUpClass(self):
        self.test_node = CalibrationNode('test_node')

    def test_name(self):
        self.assertEqual(self.test_node.name, 'test_node')

    def test_executing_node(self):
        self.assertEqual(self.test_node.state(), 'unknown')
        self.test_node.execute_node()
        self.assertEqual(self.test_node.state(), 'good')

    def test_checking_node(self):
        self.assertEqual(self.test_node.state(), 'unknown')
        check_state = self.test_node.check()
        self.assertEqual(check_state, 'needs calibration')
        self.assertEqual(self.test_node.state(), 'needs calibration')
