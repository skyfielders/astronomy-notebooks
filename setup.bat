REM set up a new virtualenv and activate it
if not exist venv virtualenv --system-site-packages venv
call venv\Scripts\activate.bat

REM iPython, and the libraries needed for it to run Notebook.
pip install ipython
pip install tornado
pip install pyzmq
pip install jinja2

REM Visualization tools and their dependencies.
pip install numpy
pip install scipy
pip install matplotlib
pip install vtk
pip install mayavi==4.3.0
pip install traits==4.3.0
pip install traitsui==4.3.0
pip install pyface==4.3.0
REM pip install wxPython

REM Tools specifically for the 'iPython Features' notebook.
pip install sympy

REM Astronomical software.
pip install pyephem
pip install jplephem
pip install de405
pip install sgp4
pip install skyfield==0.1

REM Tools specifically for the 'An-Introduction--Pandas' notebook.
REM pip install pandas # 2014-01-15 0.13.0 crashes, hence following fudge.
pip install pandas==0.12.0

REM download data sets
pip install requests
mkdir data
echo Downloading large data sets...
python download_data.py
