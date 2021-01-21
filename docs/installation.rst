.. highlight:: shell

Installation
================

All systems except Windows
-------------------------------------

Start by installing graphviz::

    $ apt install graphviz graphviz-dev

And then install AutDepGraph using pip::

    $ pip install autodepgraph


If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Windows installation can be more challenging
------------------------------------------------

Installation on windows is a bit more difficult, this relates mostly to the installation of pygraphviz. To install graphviz and pygraphviz on windows follow these steps:

- get the 64 bit version of ![graphviz for windows](https://github.com/mahkoCosmo/GraphViz_x64/), copy it to e.g., program files and add the bin folder to the system path.
- the 64 bit version lacks the libxml2.dll, you most likely have this from some other program. You can find this by searching for `libxml2.dll` in the program files folder. After that just copy paste it to the bin folder of graphviz.
- get pygraphviz by downloading the master from github.
- Now you will need to edit pygraphviz/graphviz.i and pygraphviz/graphviz_wrap.c according to the changes at https://github.com/Kagami/pygraphviz/tree/py3-windows-iobase. A reference can be found in the _install folder
- Next install using
```
python setup.py install --include-path="C:\Program Files\graphviz-2.38_x64\include" --library-path="C:\Program Files\graphviz-2.38_x64\lib"
```

- then install autodepgraph and test the installation using `py.test`
