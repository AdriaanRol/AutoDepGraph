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


def create_rabi_sims_example_graph():
    rmg = g.Graph('Rabi_sims_example_graph')

    nodenames = ['mixer_offset', 'mixer_skewness', 'frequency_spec',
                 'Amplitude_coarse', 'SSRO', 'frequency_ramsey', 'Motzoi',
                 'Amplitude_fine', 'High_fidelity_single_qubit_gates',
                 'High_readout_fidelity', 'Chevron_amp', 'Trotter_chevron',
                 'Photon_meter', 'Wigner_tomography', 'Rabi_simulation']
    for nodename in nodenames:
        rmg.add_node(nodename)
        rmg.nodes[nodename].calibrate_function('test_calibration_True')
        rmg.nodes[nodename].check_function('always_needs_calibration')

    rmg.mixer_skewness.parents(['mixer_offset'])
    rmg.Amplitude_coarse.parents(['frequency_spec',
                                  'mixer_offset', 'mixer_skewness'])
    rmg.SSRO.parents(['Amplitude_coarse'])
    rmg.frequency_ramsey.parents(['Amplitude_coarse', 'SSRO',
                                  'frequency_spec'])

    rmg.Motzoi.parents(['Amplitude_coarse', 'frequency_ramsey'])
    rmg.Amplitude_fine.parents(['Motzoi'])
    rmg.High_fidelity_single_qubit_gates.parents(
        ['Amplitude_fine', 'Motzoi', 'frequency_ramsey'])
    rmg.High_readout_fidelity.parents(
        ['High_fidelity_single_qubit_gates', 'SSRO'])
    rmg.Chevron_amp.parents(
        ['High_fidelity_single_qubit_gates', 'High_readout_fidelity'])
    rmg.Trotter_chevron.parents(['Chevron_amp'])
    rmg.Photon_meter.parents(['Trotter_chevron'])
    rmg.Wigner_tomography.parents(['Photon_meter'])
    rmg.Rabi_simulation.parents(
        ['Wigner_tomography', 'Photon_meter',
         'High_fidelity_single_qubit_gates', 'High_readout_fidelity'])
    rmg.save_graph(os.path.join(test_dir, 'rabi_sims_example_graph.yaml'))


create_rabi_sims_example_graph()
