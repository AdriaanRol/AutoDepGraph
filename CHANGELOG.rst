==============
Changelog
==============

0.4.0 (2021-01-22)
------------------
* Migrated to gitlab and set up gitlab-ci for tests.
* Set up sphinx documentation.
* Improved error message for invalid node states.
* Updated docstring for maintaining nodes.
* Fixed a bug where the svg_viewer was not packaged making the pip installed version of this package not work.


0.3.5 (2020-08-12)
------------------
* Added calibration function arguments.


0.3.3 (2019-03-15)
------------------
* Allow custom positions of node locations in graphs to allow package to function without pygraphviz.


0.3.2 (2018-05-19)
------------------
* Updated qcodes dependency
* Added DOI badge


0.3 (2018-05-18)
------------------
* NetworkX based rewrite of AutoDepGraph.
* Added SVG based visualization and viewer.
* Removed deprecated pyqtgraph imports when not used.

* Misc fixes and convenience functions.

    - add function to open html viewer
    - improve error handling
    - add version to package
    - added convenience function set set node description
    - added function calibration_state. this is used to add a QCoDeS parameter like

0.2 (2018-05-18)
------------------
* Broken release on PyPI (released as 0.3.0)

0.1.1 (2018-03-09)
------------------
* Added reference to Kelly ArXiv paper.

0.1.0 (2017-11-10)
------------------

* First release on PyPI.
* A fully functional release of the basic functionality.
