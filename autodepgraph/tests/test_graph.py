from unittest import TestCase
from copy import deepcopy
import autodepgraph as adg
from autodepgraph.graph import CalibrationNode, Graph
import yaml
import os
test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')


class Test_Graph(TestCase):

    @classmethod
    def setUpClass(self):
        self.node_A = CalibrationNode('A')
        self.node_B = CalibrationNode('B')
        self.node_C = CalibrationNode('C')
        self.node_D = CalibrationNode('D')

    def test_adding_node(self):
        test_graph = Graph('test_graph_adding_node')
        nodes_before = test_graph._nodes
        self.assertEqual(len(nodes_before.keys()), 0)
        test_graph.add_node(self.node_A)
        nodes_after = test_graph._nodes
        self.assertEqual(nodes_after, {self.node_A.name: self.node_A})

        # Adding the same node multiple times
        test_graph.add_node(self.node_A)
        test_graph.add_node(self.node_A)
        nodes_after = test_graph._nodes
        self.assertEqual(nodes_after, {self.node_A.name: self.node_A})

    def test_save_graph(self):
        test_graph = Graph('test_graph_saving')

        test_graph.add_node(self.node_A)
        test_graph.add_node(self.node_B)
        test_graph.add_node(self.node_C)
        snap = test_graph.snapshot()
        fn = os.path.join(test_dir, 'tg.yaml')
        test_graph.save_graph(filename=fn)
        f = open(fn)
        loaded_snap = yaml.safe_load(f)
        f.close()

        self.assertEqual(snap, loaded_snap)
        self.assertEqual(set(loaded_snap),
                         set(['nodes', 'meta']))
        self.assertEqual(set(loaded_snap['nodes']),
                         set(['A', 'B', 'C']))
        # Could also test if the values of the attributes are identical

    def test_loading_graph_from_file(self):

        fn = os.path.join(test_dir, 'test_graph_new_nodes.yaml')
        new_graph = Graph('new_graph')
        new_graph.load_graph(fn, load_node_state=False)
        # Test that both graphs refer to the same (existing) objects.
        self.assertEqual(set(new_graph._nodes.keys()),
                         set(['A', 'B', 'E', 'F']))
        for nodename, node in new_graph._nodes.items():
            self.assertEqual(node.state(), 'unknown')

        new_graph_2 = Graph('new_graph_2')
        new_graph_2.load_graph(fn, load_node_state=True)
        self.assertEqual(set(new_graph_2._nodes.keys()),
                         set(['A', 'B', 'E', 'F']))
        A = new_graph_2._nodes['A']
        B = new_graph_2._nodes['B']
        E = new_graph_2._nodes['E']

        self.assertEqual(A.state(), 'good')
        self.assertEqual(B.state(), 'bad')
        self.assertEqual(E.state(), 'unknown')

        # TODO: add a test for also loading functions

    @classmethod
    def tearDownClass(self):
        # finds and closes all qcodes instruments
        all_instrs = deepcopy(list(self.node_A._all_instruments.keys()))
        for insname in all_instrs:
            try:
                self.node_A.find_instrument(insname).close()
            except KeyError:
                pass

