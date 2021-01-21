===============
User guide
===============


AutoDepGraph consists of two main classes, the CalibrationNode and the Graph.
Calibration is done by calling a node that one wants to execute, the node contains the logic required to satisfy the nodes it depends on (parents).

Nodes
=========

A CalibrationNode contains:

- parameters
    - state
        + Good (green): check passes
        + needs calibration (yellow): calibration is not up to date anymore and needs to be updated
        + Bad (red): calibration or check has failed
        + unknown (grayed): checks of the node should be run
        + active (blue): calibration or check in progress
    - parents: the nodes it depends on
    - children: nodes that depend on this node
    - check_function : name of function to be executed when check is called. This can be a method of another instrument.
    - calibrate_function : name of function to be executed when calibrate is called. This can be a method of another instrument.
    - calibration_timeout: time in (s) after which a calibration times out.

- function
    - execute or call
        + Performs the logic of a node (check state, satisfy requirements) with the goal of moving to a "good" state
    - check
        + Performs checks to determine and the state of a node
    - calibrate
        + Executes the calibration routines of the node

Graphs
==========

A Graph is a container of nodes, it is used for:
- new graphs can be created by instantiating a graph and then using the add_node method to define new nodes.
- loading and saving the graph
- real-time visualization using pyqtgraph
    - state of the node determines color of a node
    - if a node has no calibrate function defined it is a manual node and has a hexagonal instead of a circle as symbol
    - mouseover information lists more properties (planned)
