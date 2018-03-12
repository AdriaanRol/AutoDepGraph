from unittest import TestCase
import autodepgraph as adg
from autodepgraph.graph_v2 import AutoDepGraph_DAG
import yaml
import os
test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')


class Test_Graph(TestCase):

    @classmethod
    def setUpClass(self):
        cal_True_delayed= ('autodepgraph.node_functions.calibration_functions'
            '.test_calibration_True_delayed')
        test_graph = AutoDepGraph_DAG('test graph')
        for node in ['A', 'B', 'C', 'D', 'E']:
            test_graph.add_node(node, calibrate_function=cal_True_delayed)
        test_graph.add_edge('C', 'A')
        test_graph.add_edge('C', 'B')
        test_graph.add_edge('B', 'A')
        test_graph.add_edge('D', 'A')
        test_graph.add_edge('E', 'D')
        self.test_graph= test_graph

    def test_save_graph(self):
        pass

    def test_load_graph(self):
        pass

    def test_tolerance_check(self):
        pass

    def test_execute_node_assume_unkown_is_good(self):
        self.test_graph.set_all_node_states(
            'unknown')
        self.test_graph.execute_node('C')
        self.assertEqual(self.test_graph.nodes()['C']['state'], 'good')
        self.assertEqual(self.test_graph.nodes()['B']['state'], 'unknown')

    def test_execute_node_require_cal(self):
        self.test_graph.set_all_node_states(
            'needs calibration')
        self.test_graph.execute_node('C')
        self.assertEqual(self.test_graph.nodes()['C']['state'], 'good')
        self.assertEqual(self.test_graph.nodes()['B']['state'], 'good')
        self.assertEqual(self.test_graph.nodes()['D']['state'],
                         'needs calibration')



    def test_plotting_mpl(self):
        self.test_graph.draw_mpl()


