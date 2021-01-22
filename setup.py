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


with open('CHANGELOG.rst') as history_file:
    history = history_file.read()


with open('requirements.txt') as reqs:
    requirements = reqs.read().splitlines()


with open('README.rst') as readme_file:
    readme = readme_file.read()


def license():
    with open('LICENSE') as f:
        return f.read()


setup_requirements = ['pytest-runner', 'wheel', ]

test_requirements = ['pytest>=3',]

setup(name='autodepgraph',
      version=get_version(),
      python_requires='>=3.6',
      description='Framework for automated calibrations based on a directed acyclic graph.',
      long_description=readme + '\n\n' + history,
      long_description_content_type='text/markdown',
      author='Adriaan Rol et al.',
      author_email='adriaan.rol@gmail.com',
      packages=find_packages(),
      ext_package='autodepgraph',
      license='MIT',
      install_requires=requirements,
      setup_requires=setup_requirements,
      test_suite='tests',
      tests_require=test_requirements,
      keywords=['graph', 'calibration framework'],
      url='https://gitlab.com/AdriaanRol/AutoDepGraph',
      classifiers=['Development Status :: 4 - Beta', 'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'License :: OSI Approved :: MIT License',
                   ]
      )
