import autodepgraph as adg
import autodepgraph.graph as g
import autodepgraph.node as n
import os

############################################
# This file generates and saves predefined
# graphs used in the tests.
############################################

test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')

# Write graph for test_graph

nodeA = n.CalibrationNode('A')
nodeB = n.CalibrationNode('B')
nodeE = n.CalibrationNode('E')
nodeF = n.CalibrationNode('F')

a = g.Graph('new_graph')
a.add_node(nodeA)
a.add_node(nodeB)
a.add_node(nodeE)
a.add_node(nodeF)

nodeA.state('good')
nodeB.state('bad')
nodeE.state('unknown')

a.save_graph(os.path.join(test_dir, 'test_graph_new_nodes.yaml'))

# Write graph for test_visualization

nodeC = n.CalibrationNode('C')
nodeD = n.CalibrationNode('D')
nodeG = n.CalibrationNode('G')
nodeH = n.CalibrationNode('H')

a.add_node('C')
a.add_node('D')
a.add_node('G')
a.add_node('H')

nodeA.state('unknown')
nodeB.state('unknown')
nodeE.state('unknown')

nodeD.add_parent('C')
nodeD.add_parent('A')
nodeE.add_parent('D')
nodeG.add_parent('F')
nodeC.add_parent('B')
nodeB.add_parent('A')
nodeG.add_parent('D')
nodeH.add_parent('G')

a.save_graph(os.path.join(test_dir, 'test_graph_states.yaml'))

for node in a.nodes.values():
    node.close()

a.close()
