from unittest import TestCase
import autodepgraph as adg
from autodepgraph.graph import CalibrationNode, Graph
import yaml
import os
test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')


class Test_Node(TestCase):
    @classmethod
    def setUpClass(self):
        self.node_A = CalibrationNode('A')
        self.node_B = CalibrationNode('B')
        self.node_C = CalibrationNode('C')
        self.node_D = CalibrationNode('D')

    def test_adding_node(self):
        test_graph = Graph('test_graph_adding_node')
        nodes_before = test_graph._nodes
        self.assertEqual(len(nodes_before), 0)
        test_graph.add_node(self.node_A)
        nodes_after = test_graph._nodes
        self.assertEqual(nodes_after, [self.node_A])

    def test_save_graph(self):
        test_graph = Graph('test_graph_saving')

        test_graph.add_node(self.node_A)
        test_graph.add_node(self.node_B)
        test_graph.add_node(self.node_C)
        snap = test_graph.snapshot()
        fn = os.path.join(test_dir, 'tg.yaml')
        test_graph.save_graph(filename=fn)
        f = open(fn)
        loaded_snap = yaml.load(f)
        f.close()

        self.assertEqual(snap, loaded_snap)
        self.assertEqual(set(loaded_snap),
                         set(['nodes', 'meta']))
        self.assertEqual(set(loaded_snap['nodes']),
                         set(['A', 'B', 'C']))
        # Could also test if the values of the attributes are identical

    def test_loading_graph_from_file(self):
        # Save the existing graph
        # test_graph = Graph('test_graph_loading')

        # test_graph.add_node(self.node_A)
        # test_graph.add_node(self.node_B)

        # test_graph.add_node(CalibrationNode('E'))
        # test_graph.add_node(CalibrationNode('F'))

        fn = os.path.join(test_dir, 'test_graph_new_nodes.yaml')
        # test_graph.save_graph(filename=fn)

        new_graph = Graph('new_graph')
        new_graph.load_graph(fn)
        # Test that both graphs refer to the same (existing) objects.
        self.assertEqual(set([node.name for node in new_graph._nodes]),
                         set(['A', 'B', 'E', 'F']))

        # # Test that loading works when a node was closed but not deleted.
        # # self.node_D.close()
        # new_graph.load_graph(fn)
        # # Test that both graphs refer to the same (existing) objects.
        # self.assertEqual(set(new_graph._nodes), set(self.test_graph._nodes))
        # test_graph.close()
        # new_graph.close()




        # pass

