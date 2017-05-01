import os
import qcodes as qc
from autodepgraph.graph import Graph
from autodepgraph.visualization import snapshot_to_nxGraph
import unittest
from unittest import TestCase
import autodepgraph as adg
test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')


class Test_visualization(TestCase):

    @classmethod
    def setUpClass(self):
        fn = os.path.join(test_dir, 'test_graph_states.yaml')
        self.test_graph = Graph('test_graph')
        self.test_graph.load_graph(fn, load_node_state=True)

    def test_snapshot_to_nxGraph(self):
        snap = self.test_graph.snapshot()
        nxG = snapshot_to_nxGraph(snap)
        self.assertEqual(set(nxG.nodes()),
                         set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']))
        dep_edges = set([('D', 'C'), ('D', 'A'), ('E', 'D'), ('G', 'F'),
                        ('C', 'B'), ('B', 'A'), ('G', 'D'), ('H', 'G')])
        self.assertEqual(set(nxG.edges()), dep_edges)

    @unittest.skip('Test not impemented')
    def test_get_state_col_map(self):
        raise NotImplementedError()

    @unittest.skip('Test not impemented')
    def test_draw_graph_mpl(self):
        raise NotImplementedError()

    @classmethod
    def tearDownClass(self):
        # finds and closes all qcodes instruments
        all_instrs = (list(qc.Instrument._all_instruments.keys()))
        for insname in all_instrs:
            try:
                qc.Instrument.find_instrument(insname).close()
            except KeyError:
                pass
