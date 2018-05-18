import autodepgraph as adg
from autodepgraph.graph_v2 import AutoDepGraph_DAG
import autodepgraph.node as n
import networkx as nx
import os


############################################
# This file generates and saves predefined
# graphs used in the tests.
############################################

test_dir = os.path.join(adg.__path__[0], 'tests', 'test_data')

# # Write graph for test_graph

# nodeA = n.CalibrationNode('A')
# nodeB = n.CalibrationNode('B')
# nodeE = n.CalibrationNode('E')
# nodeF = n.CalibrationNode('F')

# a = g.Graph('new_graph')
# a.add_node(nodeA)
# a.add_node(nodeB)
# a.add_node(nodeE)
# a.add_node(nodeF)

# nodeA.state('good')
# nodeB.state('bad')
# nodeE.state('unknown')


# a.save_graph(os.path.join(test_dir, 'test_graph_new_nodes.yaml'))

# # Write graph for test_visualization

# nodeC = n.CalibrationNode('C')
# nodeD = n.CalibrationNode('D')
# nodeG = n.CalibrationNode('G')
# nodeH = n.CalibrationNode('H')

# a.add_node('C')
# a.add_node('D')
# a.add_node('G')
# a.add_node('H')

# nodeA.state('good')
# nodeB.state('needs calibration')
# nodeD.state('bad')
# nodeE.state('unknown')
# nodeF.state('good')
# nodeC.state('active')
# nodeD.add_parent('C')
# nodeD.add_parent('A')
# nodeE.add_parent('D')
# nodeG.add_parent('F')
# nodeC.add_parent('B')
# nodeB.add_parent('A')
# nodeG.add_parent('D')
# nodeH.add_parent('G')

# for node in a.nodes.values():
#     node.calibrate_function('test_calibration_True')
# nodeC.calibrate_function('NotImplementedCalibration')
# nodeF.calibrate_function('NotImplementedCalibration')


# a.save_graph(os.path.join(test_dir, 'test_graph_states.yaml'))

# for node in a.nodes.values():
#     node.close()

# a.close()


# def create_rabi_sims_example_graph():
#     rmg = g.Graph('Rabi_sims_example_graph')

#     nodenames = ['mixer_offset', 'mixer_skewness', 'frequency_spec',
#                  'Amplitude_coarse', 'SSRO', 'frequency_ramsey', 'Motzoi',
#                  'Amplitude_fine', 'High_fidelity_single_qubit_gates',
#                  'High_readout_fidelity', 'Chevron_amp', 'Trotter_chevron',
#                  'Photon_meter', 'Wigner_tomography', 'Rabi_simulation']
#     for nodename in nodenames:
#         rmg.add_node(nodename)
#         rmg.nodes[nodename].calibrate_function('test_calibration_True')
#         rmg.nodes[nodename].check_function('always_needs_calibration')

#     rmg.mixer_skewness.parents(['mixer_offset'])
#     rmg.Amplitude_coarse.parents(['frequency_spec',
#                                   'mixer_offset', 'mixer_skewness'])
#     rmg.SSRO.parents(['Amplitude_coarse'])
#     rmg.frequency_ramsey.parents(['Amplitude_coarse', 'SSRO',
#                                   'frequency_spec'])

#     rmg.Motzoi.parents(['Amplitude_coarse', 'frequency_ramsey'])
#     rmg.Amplitude_fine.parents(['Motzoi'])
#     rmg.High_fidelity_single_qubit_gates.parents(
#         ['Amplitude_fine', 'Motzoi', 'frequency_ramsey'])
#     rmg.High_readout_fidelity.parents(
#         ['High_fidelity_single_qubit_gates', 'SSRO'])
#     rmg.Chevron_amp.parents(
#         ['High_fidelity_single_qubit_gates', 'High_readout_fidelity'])
#     rmg.Trotter_chevron.parents(['Chevron_amp'])
#     rmg.Photon_meter.parents(['Trotter_chevron'])
#     rmg.Wigner_tomography.parents(['Photon_meter'])
#     rmg.Rabi_simulation.parents(
#         ['Wigner_tomography', 'Photon_meter',
#          'High_fidelity_single_qubit_gates', 'High_readout_fidelity'])
#     rmg.save_graph(os.path.join(test_dir, 'rabi_sims_example_graph.yaml'))


# create_rabi_sims_example_graph()

class Qubit():
    def __init__(self,  name):
        self.name = name


class Device():
    def __init__(self,  name, qubits):
        self.name = name
        self.qubits = qubits


def create_dep_graph_single_qubit(self):
    print(self.name+' DAG')
    DAG = AutoDepGraph_DAG(name=self.name+' DAG')

    DAG.add_node(self.name+' resonator frequency')
    DAG.add_node(self.name+' frequency coarse')
    DAG.add_edge(self.name+' frequency coarse',
                 self.name+' resonator frequency')

    DAG.add_node(self.name+' mixer offsets drive')
    DAG.add_node(self.name+' mixer skewness drive')
    DAG.add_node(self.name+' mixer offsets readout')

    DAG.add_node(self.name + ' pulse amplitude coarse')
    DAG.add_edge(self.name + ' pulse amplitude coarse',
                 self.name+' frequency coarse')
    DAG.add_edge(self.name + ' pulse amplitude coarse',
                 self.name+' mixer offsets drive')
    DAG.add_edge(self.name + ' pulse amplitude coarse',
                 self.name+' mixer skewness drive')
    DAG.add_edge(self.name + ' pulse amplitude coarse',
                 self.name+' mixer offsets readout')

    DAG.add_node(self.name+' T1')
    DAG.add_node(self.name+' T2-echo')
    DAG.add_node(self.name+' T2-star')
    DAG.add_edge(self.name + ' T1', self.name+' pulse amplitude coarse')
    DAG.add_edge(self.name + ' T2-echo', self.name+' pulse amplitude coarse')
    DAG.add_edge(self.name + ' T2-star', self.name+' pulse amplitude coarse')

    DAG.add_node(self.name+' frequency fine')
    DAG.add_edge(self.name + ' frequency fine',
                 self.name+' pulse amplitude coarse')

    DAG.add_node(self.name + ' pulse amplitude med')
    DAG.add_edge(self.name + ' pulse amplitude med',
                 self.name+' frequency fine')

    DAG.add_node(self.name + ' optimal weights')
    DAG.add_edge(self.name + ' optimal weights',
                 self.name+' pulse amplitude med')

    DAG.add_node(self.name+' gates restless')
    DAG.add_edge(self.name + ' gates restless', self.name+' optimal weights')

    # easy to implement a check
    DAG.add_node(self.name+' frequency fine')

    DAG.add_node(self.name+' room temp. dist. corr.')
    DAG.add_node(self.name+' cryo dist. corr.')
    DAG.add_edge(self.name+' cryo dist. corr.',
                 self.name+' room temp. dist. corr.')

    DAG.add_edge(self.name+' cryo dist. corr.',
                 self.name+' gates restless')
    # DAG.add_node(self.name+' ')

    return DAG


def create_dep_graph_device(self, dags):
    DAG = nx.compose_all(dags)

    DAG.add_node(self.name+' multiplexed readout')
    DAG.add_node(self.name+' resonator frequencies coarse')
    DAG.add_node('AWG8 MW-staircase')
    DAG.add_node('AWG8 Flux-staircase')
    DAG.add_node('Chevron q0-q1')
    DAG.add_node('Chevron q1-q2')
    DAG.add_node('CZ q0-q1')
    DAG.add_node('CZ q1-q2')

    DAG.add_edge('CZ q0-q1', 'Chevron q0-q1')
    DAG.add_edge('CZ q1-q2', 'Chevron q1-q2')

    DAG.add_edge('CZ q0-q1', 'q0 cryo dist. corr.')
    DAG.add_edge('CZ q0-q1', 'q1 cryo dist. corr.')

    DAG.add_edge('CZ q1-q2', 'q1 cryo dist. corr.')
    DAG.add_edge('CZ q1-q2', 'q2 cryo dist. corr.')

    DAG.add_edge('Chevron q0-q1', 'q0 gates restless')
    DAG.add_edge('Chevron q0-q1', 'AWG8 Flux-staircase')
    DAG.add_edge('Chevron q0-q1', 'q1 gates restless')
    DAG.add_edge('Chevron q0-q1', self.name+' multiplexed readout')
    DAG.add_edge('Chevron q1-q2', 'q0 gates restless')
    DAG.add_edge('Chevron q1-q2', 'AWG8 Flux-staircase')
    DAG.add_edge('Chevron q1-q2', 'q1 gates restless')
    DAG.add_edge('Chevron q1-q2', self.name+' multiplexed readout')

    for qubit in self.qubits:
        q_name = qubit.name
        DAG.add_edge(q_name+' room temp. dist. corr.',
                     'AWG8 Flux-staircase')
        DAG.add_edge(self.name+' multiplexed readout',
                     q_name+' optimal weights')

        DAG.add_edge(q_name+' resonator frequency',
                     self.name+' resonator frequencies coarse')
        DAG.add_edge(q_name+' pulse amplitude coarse', 'AWG8 MW-staircase')
    return DAG


qubit_names = ['q0', 'q1', 'q2']
qubits = []
dags = []
for qubit_name in qubit_names:
    qi = Qubit(qubit_name)
    qubits.append(qi)
    dep_graph = create_dep_graph_single_qubit(qi)
    dags.append(dep_graph)

device = Device('3 qubit device', qubits)

device_dag = create_dep_graph_device(device, dags)
for node, attrs in device_dag.nodes(True):
    attrs['calibrate_function'] = 'autodepgraph.node_functions.calibration_functions.test_calibration_True'

device_dag.draw_svg()
fn = os.path.join(test_dir, 'three_qubit_graph.yaml')
nx.readwrite.write_yaml(device_dag, fn)
