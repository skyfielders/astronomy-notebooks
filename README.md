astronomy-notebooks
===================

iPython Notebooks showing off NumPy, matplotlib, and our universe

Getting Started
---------------
The short version: make sure you have all of the appropriate dependencies installed and then run the appropriate setup script for your platform.

### Linux
1. Install/build the required dependencies. Most dependencies other than Python and virtualenv are automatically installed via the setup script.
2. Clone or fork this repo.
3. Run setup.sh to set up a new virtualenv and download required data sets.

### Windows
1. Install the required dependencies. See below for details.
2. Clone or fork this repo.
3. Run setup.bat to create a new virtualenv, install any missing dependencies, and download required data sets.

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
