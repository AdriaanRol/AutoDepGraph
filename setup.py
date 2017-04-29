
from distutils.core import setup


setup(name='autodepgraph',
      version='0.1',
      description='automated tuning based on dependency graph',
      author='Adriaan Rol et al',
      author_email='adriaan.rol@gmail.com',
      packages=['autodepgraph'],
      ext_package='autodepgraph',
      requires=["pytools", "numpy(>=1.12)", "pytest", "pytest.cov", "matplotlib"]
      )
