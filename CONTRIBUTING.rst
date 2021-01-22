.. highlight:: shell

============
Contributing
============

Contributions are welcome and greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Reporting of Bugs and Defects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A defect is any variance between actual and expected result, this can include bugs in the code or defects in the documentation or visualization.

Please report defects to the `the GitLab Tracker <https://gitlab.com/AdriaanRol/AutoDepGraph/-/issues>`_
using the **Defect** description template.

`Merge Request Guidelines`_ for details on best developmental practices.

Features
~~~~~~~~

If you wish to propose a feature, please file an issue on `the GitLab Tracker <https://gitlab.com/AdriaanRol/AutoDepGraph/-/issues>`_ using the **Feature** description template. Community members will help refine and design your idea until it is ready for implementation.
Via these early reviews, we hope to steer contributors away from producing work outside of the project boundaries.

Please see the `Merge Request Guidelines`_ for details on best developmental practices.

Documentation
~~~~~~~~~~~~~

AutoDepGraph could always use more documentation, whether as part of the official AutoDepGraph docs, in docstrings, tutorials and even on the web in blog posts, articles and such.

For docstrings, please use the `numpy docstring format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.

Working on issues
------------------

After an issue is created, the progress of the issues is tracked on the `GitLab issue board <https://gitlab.com/AdriaanRol/AutoDepGraph/-/issues>`_.
The maintainers will update the state using `labels <https://gitlab.com/AdriaanRol/AutoDepGraph/-/labels>`_ .
Once an issue is ready for review a Merge Request can be opened.



Merge Request Guidelines
--------------------------

Please make merge requests into the *develop* branch (not the *master* branch). Each request should be self-contained and address a single issue on the tracker.

Before you submit a merge request, check that it meets these guidelines:

1. New code should be fully tested; running pytest in coverage mode can help identify gaps.
2. Documentation is updated, this includes docstrings and any necessary changes to existing tutorials, user documentation and so forth. We use the `numpy docstring format <https://numpydoc.readthedocs.io/en/latest/format.html>`_.
3. The CI pipelines should pass for all merge requests.

   - Check the status of the pipelines, the status is also reported in the merge request.
   - flake8 linter should pass.
   - No degradation in code coverage.
   - Documentation should build.
4. Ensure your merge request contains a clear description of the changes made and how it addresses the issue. If useful, add a screenshot to showcase your work to facilitate an easier review.

Congratulations! The maintainers will now review your work and suggest any necessary changes.
If no changes are required, a maintainer will "approve" the review.
If you are
Thank you very much
for your hard work in improving AutoDepGraph.