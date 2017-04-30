import os
from autodepgraph.graph import Graph
from copy import deepcopy
from autodepgraph.visualization import snapshot_to_nxGraph
from unittest import TestCase
import autodepgraph as adg
test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')


class Test_visualization(TestCase):

    @classmethod
    def setUpClass(self):
        # self.node_A = CalibrationNode('A')

        fn = os.path.join(test_dir, 'test_graph_new_nodes.yaml')
        self.test_graph = Graph('test_graph')
        print(self.test_graph._nodes)
        self.test_graph.load_graph(fn, load_node_state=False)
        self.node_A = self.test_graph._nodes['A']
        print(self.test_graph._nodes)

    def test_snapshot_to_nxGraph(self):
        snap = self.test_graph.snapshot()
        print(self.test_graph._nodes)
        nxG = snapshot_to_nxGraph(snap)
        self.assertEqual(set(nxG.nodes()), set(['A', 'B',  'E', 'F']))
        self.assertEqual(set(nxG.edges()), set([('B', 'A')]))

    def test_get_state_col_map(self):
        raise NotImplementedError()

    def draw_graph_mpl(self):
        raise NotImplementedError()

    @classmethod
    def tearDownClass(self):
        # finds and closes all qcodes instruments
        all_instrs = deepcopy(list(self.node_A._all_instruments.keys()))
        for insname in all_instrs:
            try:
                self.node_A.find_instrument(insname).close()
            except KeyError:
                pass
