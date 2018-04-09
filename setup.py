import re
from setuptools import setup

def get_version(verbose=1):
    """ Extract version information from source code """

    try:
        with open('autodepgraph/version.py', 'r') as f:
            ln = f.readline()
            m = re.search('.* ''(.*)''', ln)
            version = (m.group(1)).strip('\'')
    except Exception as E:
        print(E)
        version = 'none'
    if verbose:
        print('get_version: %s' % version)
    return version

version = get_version()

setup(name='autodepgraph',
      version=version,
      description='automated tuning based on dependency graph',
      author='Adriaan Rol et al',
      author_email='adriaan.rol@gmail.com',
      packages=['autodepgraph'],
      ext_package='autodepgraph',
      requires=["qcodes", "pytools", "numpy(>=1.12)", "pytest", "pytest.cov", "matplotlib"]
      )
