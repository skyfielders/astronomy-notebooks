REM set up a new virtualenv and activate it
if not exist venv virtualenv --system-site-packages venv
call venv\Scripts\activate.bat

REM iPython, and the libraries needed for it to run Notebook.
pip install ipython
pip install tornado
pip install pyzmq

REM Visualization tools and their dependencies.
pip install numpy
pip install scipy
pip install matplotlib
pip install vtk
pip install mayavi
REM pip install wxPython

REM Tools specifically for the 'iPython Features' notebook.
pip install sympy

REM Astronomical software.
pip install pyephem
pip install jplephem
pip install de405
pip install sgp4

REM download data sets
pip install requests
mkdir data
python download_data.py
