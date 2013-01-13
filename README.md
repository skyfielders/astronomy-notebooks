astronomy-notebooks
===================

iPython Notebooks showing off NumPy, matplotlib, and our universe

Dependencies
------------

#### iPython
- ipython, tornado, pyzmq
- sympy (only required for the 'iPython Features' notebook)

#### Visualization tools
- numpy, scipy, matplotlib
- [VTK][vtk] (see notes below)
- mayavi (may need to be compiled from source?)
- wxPython

#### Astronomical software
- pyephem
- jplephem
- de405
- sgp4

#### Data sets
- [HYG star database][hyg]

#### VTK
- VTK must be compiled from source to include python support, which requires [CMake][cmake] and a compiler
- Building VTK, depending on the options used, may have additional dependencies and will probably take forever
- VTK needs to be built before running the setup script
- In Windows, Visual Studio Express will build VTK but installing the Python package is still a non-trivial process

[vtk]: http://www.vtk.org/VTK/resources/software.html
[cmake]: http://www.cmake.org/
[hyg]: https://github.com/astronexus/HYG-Database
