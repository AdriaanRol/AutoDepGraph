================
AutoDepGraph
================


.. image:: https://gitlab.com/AdriaanRol/AutoDepGraph/badges/develop/pipeline.svg
    :target: https://gitlab.com/AdriaanRol/AutoDepGraph/pipelines/

.. image:: https://img.shields.io/pypi/v/autodepgraph.svg
    :target: https://pypi.python.org/pypi/autodepgraph
    :alt: PyPI

.. image:: https://gitlab.com/AdriaanRol/AutoDepGraph/badges/develop/coverage.svg
    :target: https://gitlab.com/AdriaanRol/AutoDepGraph/pipelines/

.. image:: https://readthedocs.com/projects/autodepgraph/badge/?version=latest
    :target: https://autodepgraph.readthedocs-hosted.org/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/badge/License-MIT-blue.svg
    :target: https://gitlab.com/AdriaanRol/AutoDepGraph/-/blob/master/LICENSE
.. image:: https://zenodo.org/badge/85987885.svg
    :target: https://zenodo.org/badge/latestdoi/85987885
    :alt: DOI


AutoDepGraph is a framework for using dependency graphs to calibrate a system. It is inspired by `"Physical qubit calibration on a directed acyclic graph" <https://arxiv.org/abs/1803.03226>`_.

Overview
================

AutoDepGraph consists of two main classes, the CalibrationNode and the Graph.
Calibration is done by calling a node that one wants to execute, the node contains the logic required to satisfy the nodes it depends on (parents).

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

A Graph is a container of nodes, it is used for:
- new graphs can be created by instantiating a graph and then using the add_node method to define new nodes.
- loading and saving the graph
- real-time visualization using pyqtgraph
    - state of the node determines color of a node
    - if a node has no calibrate function defined it is a manual node and has a hexagonal instead of a circle as symbol
    - mouseover information lists more properties (planned)

![Example calibration graph](docs/example_graph.png)

Examples
================

For an introductory example see the example notebook. If you want to see how to use a specific function, see the tests located in the autodepgraph/tests folder.



Acknowledgements
================================

I would like to thank Julian Kelly for the idea of using a dependency graph for calibrations and for early discussions. I would like to thank Joe Weston for discussions and help in working out the initial design. I would like to acknowledge Livio Ciorciaro for disucssions and as a coauthor of this project.
