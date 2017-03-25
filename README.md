# AutoDepGraph [![Build Status](https://travis-ci.org/AdriaanRol/AutoDepGraph.svg?branch=master)]
A very nondescript name for a WIP on dependency graph based tuning 

## Requirements
Calibration is done by calling a node that we want to execute. 
A node contains 
- attributes
    - state     
        + Good (green)
        + needs calibration (yellow)
        + Bad/broken (red)
        + Requires check (grayed out color of last known state) 
        + In progress/active (blue)
    - 
- function
    - execute
        + Performs the logic of a node (check state, satisfy requirements)
    - check status
        + Performs a quick check to determine and set the state
    - calibrate 
        + Performs the 

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
