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
- [VTK][vtk] (must be compiled from source to include python support, which also requires [CMake][cmake] and a compiler such as Visual Studio)
- mayavi (may need to be compiled from source?)
- wxPython

#### Astronomical software
- pyephem
- jplephem
- de405
- sgp4

#### Data sets
- [HYG star database][hyg]

[vtk]: http://www.vtk.org/VTK/resources/software.html
[cmake]: http://www.cmake.org/
[hyg]: https://github.com/astronexus/HYG-Database
