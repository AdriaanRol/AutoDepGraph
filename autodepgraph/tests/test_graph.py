from unittest import TestCase
import autodepgraph as adg
from autodepgraph.graph import CalibrationNode, Graph
import yaml
import os
test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')


class Test_Node(TestCase):
    @classmethod
    def setUpClass(self):
        self.test_graph = Graph('test_graph')
        self.node_A = CalibrationNode('A')
        self.node_B = CalibrationNode('B')
        self.node_C = CalibrationNode('C')

    def test_adding_node(self):
        test_graph = Graph('test_graph')
        nodes_before = test_graph._nodes
        self.assertEqual(len(nodes_before), 0)
        test_graph.add_node(self.node_A)
        nodes_after = test_graph._nodes
        self.assertEqual(nodes_after, [self.node_A])

    def test_save_graph(self):

        self.test_graph.add_node(self.node_A)
        self.test_graph.add_node(self.node_B)
        self.test_graph.add_node(self.node_C)

        snap = self.test_graph.snapshot()
        fn = os.path.join(test_dir, 'tg.yaml')
        self.test_graph.save_graph(filename=fn)
        f = open(fn)
        loaded_snap = yaml.load(f)

        self.assertEqual(snap, loaded_snap)
        self.assertEqual(set(loaded_snap),
                         set(['nodes', 'meta']))
        self.assertEqual(set(loaded_snap['nodes']),
                         set(['A', 'B', 'C']))
        # Could also test if the values of the attributes are identical

    def test_loading_creating_graph_from_file(self):
        pass

