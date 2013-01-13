astronomy-notebooks
===================

iPython Notebooks showing off NumPy, matplotlib, and our universe

Getting Started
---------------
The short version: make sure you have all of the appropriate dependencies installed and then run the appropriate setup script for your platform.

### Linux
1. Install/build the required dependencies. Most dependencies other than Python and virtualenv are automatically installed via the setup script.
2. Clone or fork this repo.
3. Run setup.sh to create a new virtualenv, install any missing dependencies, and download required data sets.

### Windows
1. Install the required dependencies. See below for details.
2. Clone or fork this repo.
3. Run setup.bat to create a new virtualenv, install any missing dependencies, and download required data sets.

#### Windows Dependencies (the simple way)
The easiest way to get all of the dependencies in Windows is to use a special Python distribution meant for scientific computing. Pick one of the following options:
- Install [Python(x,y)][pxy]. You can reduce the disk space required by only selecting the dependencies listed below (and any components required by those dependencies). Mayavi is included as part of the 'ETS' component. If you already have Python 2.7 installed, Python(x,y) may clobber your existing installation.
- Install [EPD][epd]. The [free version][epd-free] of EPD does not include Mayavi, but it does contain the tools required to build it from source. If you don't want 3D visualizations, you don't need Mayavi.

#### Windows Dependencies (the harder way)

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

[pxy]: http://code.google.com/p/pythonxy/
[epd]: http://www.enthought.com/products/epd.php
[epd-free]: http://www.enthought.com/products/epd_free.php
[vtk]: http://www.vtk.org/VTK/resources/software.html
