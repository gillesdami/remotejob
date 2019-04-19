from setuptools import setup

setup(name='remotejob',
      version='0.1.1',
      description='Run python functions in a remote docker container',
      url='https://github.com/gillesdami/remotejob',
      author='Damien GILLES',
      author_email='damien.gilles.pro@gmail.com',
      license='MIT',
      packages=['remotejob'],
      install_requires=[
          'docker',
          'Pyro4',
          'dill'
      ])
