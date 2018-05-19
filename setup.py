import re
from setuptools import setup, find_packages


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


def readme():
    with open('README.md') as f:
        return f.read()


def license():
    with open('LICENSE') as f:
        return f.read()


setup(name='autodepgraph',
      version=get_version(),
      description='automated tuning based on dependency graph',
      long_description=readme(),
      long_description_content_type='text/markdown',
      author='Adriaan Rol et al',
      author_email='adriaan.rol@gmail.com',
      packages=find_packages(),
      ext_package='autodepgraph',
      license='MIT',
      requires=["qcodes", "pytools",
                "numpy", "pytest", "matplotlib"],
      keywords=['graph', 'calibration framework'],
      url='https://github.com/AdriaanRol/AutoDepGraph',
      classifiers=['Development Status :: 4 - Beta', 'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'License :: OSI Approved :: MIT License',
                   ]
      )
