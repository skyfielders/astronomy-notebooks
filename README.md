astronomy-notebooks
===================

iPython Notebooks showing off NumPy, matplotlib, and our universe

Getting Started
---------------
The short version: make sure you have all of the appropriate dependencies installed and then run the appropriate setup script for your platform.

Dependencies
------------

#### Python
- Python (obviously), virtualenv

#### iPython
- ipython, tornado, pyzmq
- sympy (only required for the 'iPython Features' notebook)

#### Visualization tools
- numpy, scipy, matplotlib
- [VTK][vtk] (must be compiled from source to include python support)
- mayavi (may need to be compiled from source?)
- wxPython

#### Astronomical software
- pyephem, jplephem, de405, sgp4
- Large data sets required by these packages are downloaded automatically by the setup script

[vtk]: http://www.vtk.org/VTK/resources/software.html
