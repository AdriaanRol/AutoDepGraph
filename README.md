# AutoDepGraph [![Build Status](https://travis-ci.org/AdriaanRol/AutoDepGraph.svg?branch=master)]
A very nondescript name for a WIP on dependency graph based tuning

## Requirements
Calibration is done by calling a node that we want to execute.
A node contains
- attributes
    - state
        + Good (green): all checks passed
        + needs calibration (yellow): calibration is not up to date anymore and needs to be updated
        + Bad/broken (red): calibration or check has failed
        + Requires check (grayed out color of last known state): checks of the node should be run
        + active (blue): calibration or check in progress
    -
- function
    - execute
        + Performs the logic of a node (check state, satisfy requirements)
    - check status
        + Performs checks to determine and set the state
    - calibrate
        + Executes the calibration routines of the node

A calibration graph
- loading and saving the graph
- real-time visualization of the graph
    + state of the node determines color
    + mouseover information listing more properties

## Test example
The example will use a dummy qcodes instrument that emulates a heterodyne experiment (using the model function + noise) and uses the analysis on this dummy data.

## Dependence on existing packages
- [graph-tool](https://graph-tool.skewed.de/), this package seems ideal but requires C-compilation (which can be painful on windows systems). Given the lightweight nature of this application I do not want to have such a heavy dependence.
- [doit](http://pydoit.org/) a python based
