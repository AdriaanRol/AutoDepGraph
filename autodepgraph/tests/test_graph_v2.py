from unittest import TestCase
import autodepgraph as adg
import networkx as nx
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

    def test_tolerance_check(self):
        # The default check returns 1.0
        self.test_graph.nodes['A']['tolerance'] = 0
        self.assertEqual(self.test_graph.check_node('A'), 'needs calibration')
        self.test_graph.nodes['A']['tolerance'] = 2
        self.assertEqual(self.test_graph.check_node('A'), 'good')
        self.test_graph.nodes['A']['tolerance'] = 0
        self.assertEqual(self.test_graph.check_node('A'), 'needs calibration')

    def test_maintain_node_assume_unkown_is_good(self):
        self.test_graph.set_all_node_states(
            'unknown')
        self.test_graph.maintain_node('C')
        self.assertEqual(self.test_graph.nodes()['C']['state'], 'good')
        self.assertEqual(self.test_graph.nodes()['B']['state'], 'unknown')

    def test_maintain_node_require_cal(self):
        self.test_graph.set_all_node_states(
            'needs calibration')
        self.test_graph.maintain_node('C')
        self.assertEqual(self.test_graph.nodes()['C']['state'], 'good')
        self.assertEqual(self.test_graph.nodes()['B']['state'], 'good')
        self.assertEqual(self.test_graph.nodes()['D']['state'],
                         'needs calibration')

    def test_bad_node(self):
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

        test_graph.set_all_node_states('unknown')

        self.assertEqual(test_graph.nodes()['C']['state'], 'unknown')
        self.assertEqual(test_graph.nodes()['B']['state'], 'unknown')
        self.assertEqual(test_graph.nodes()['A']['state'], 'unknown')

        cal_False= ('autodepgraph.node_functions.calibration_functions'
            '.test_calibration_False')
        test_graph.node['C']['calibrate_function'] = cal_False

        # Failure to calibrate should raise an error
        with self.assertRaises(ValueError):
            test_graph.maintain_node('C')
        # In the process of trying to fix node C it should try to
        # calibrate it's requirements
        self.assertEqual(test_graph.nodes()['C']['state'], 'bad')
        self.assertEqual(test_graph.nodes()['B']['state'], 'good')
        self.assertEqual(test_graph.nodes()['A']['state'], 'good')
        cal_True_delayed= ('autodepgraph.node_functions.calibration_functions'
            '.test_calibration_True_delayed')




    def test_plotting_mpl(self):
        self.test_graph.draw_mpl()

        self.test_graph.cfg_plot_mode = 'matplotlib'
        self.test_graph.update_monitor()
        # call twice to have both creation and update of plot
        self.test_graph.update_monitor()

    def test_plotting_pg(self):
        self.test_graph.draw_pg()

        self.test_graph.cfg_plot_mode = 'pyqtgraph'
        self.test_graph.update_monitor()
        # call twice to have both creation and update of plot
        self.test_graph.update_monitor()

    def test_plotting_svg(self):
        self.test_graph.draw_svg()

        self.test_graph.cfg_plot_mode = 'svg'
        self.test_graph.update_monitor()
        # call twice to have both creation and update of plot
        self.test_graph.update_monitor()


    def test_dummy_cal_three_qubit_graph(self):
        fn = os.path.join(test_dir, 'three_qubit_graph.yaml')
        DAG = nx.readwrite.read_yaml(fn)
        DAG.set_all_node_states('needs calibration')
        DAG.cfg_plot_mode = None
        DAG.maintain_node('Chevron q0-q1')

        self.assertEqual(DAG.get_node_state('Chevron q0-q1'), 'good')
        self.assertEqual(DAG.get_node_state('CZ q0-q1'), 'needs calibration')

    def test_write_read_yaml(self):
        """
        Mostly an example on how to read and write, but also test for
        weird objects being present.
        """

        self.test_graph.nodes()['C']['state'] = 'good'
        self.test_graph.nodes()['B']['state'] = 'unknown'
        fn = os.path.join(test_dir, 'nx_test_graph.yaml')
        nx.readwrite.write_yaml(self.test_graph, fn)
        read_testgraph = nx.readwrite.read_yaml(fn)

        self.assertTrue(isinstance(read_testgraph, AutoDepGraph_DAG))

        self.assertEqual(read_testgraph.nodes()['C']['state'], 'good')
        self.assertEqual(read_testgraph.nodes()['B']['state'], 'unknown')

