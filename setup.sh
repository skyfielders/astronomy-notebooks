#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")

if [ ! -d venv ]
then
    virtualenv --system-site-packages venv
fi

pip freeze >requirements.00.txt
source venv/bin/activate
pip freeze >requirements.01.txt
pip install --upgrade distribute
pip freeze >requirements.02.distribute.txt

# iPython, and the libraries needed for it to run Notebook.
pip install ipython
pip freeze >requirements.03.ipython.txt
pip install tornado
pip freeze >requirements.04.tornado.txt
pip install pyzmq
pip freeze >requirements.05.pyzma.txt
pip install jinja2
pip freeze >requirements.06.jinja2.txt

# Visualization tools and their dependencies.
pip install numpy
pip freeze >requirements.07.numpy.txt
pip install scipy
pip freeze >requirements.08.scipy.txt
pip install matplotlib
pip freeze >requirements.09.matplotlib.txt
pip install vtk
pip freeze >requirements.10.vtk.txt
pip install mayavi==4.3.0
pip freeze >requirements.11.mayavi.txt
pip install traits==4.3.0
pip freeze >requirements.12.traits.txt
pip install traitsui==4.3.0
pip freeze >requirements.13.traitsui.txt
pip install pyface==4.3.0
pip freeze >requirements.14.pyface.txt
pip install wxPython
pip freeze >requirements.15.wxPython.txt

# Tools specifically for the 'An-Introduction--Notebook-Features' notebook.
pip install sympy
pip freeze >requirements.16.sympy.txt

# Astronomical software.
pip install pyephem
pip freeze >requirements.17.pyephem.txt
pip install jplephem
pip freeze >requirements.18.jplephem.txt
pip install de405
pip freeze >requirements.19.de405.txt
pip install sgp4
pip freeze >requirements.20.sgp4.txt
pip install skyfield==0.1
pip freeze >requirements.21.skyfield.txt

# Tools specifically for the 'An-Introduction--Pandas' notebook.
# pip install pandas # 2014-01-15 0.13.0 crashes, hence following fudge.
pip install pandas==0.12.0
pip freeze >requirements.22.pandas.txt

# Get ready to download large data sets.
mkdir -p data
cd data

# As described on the http://www.astronexus.com/node/34 page, the
# following link is a star catalog now hosted on github.  HOW COOL!
wget -nc https://raw.github.com/astronexus/HYG-Database/master/hygfull.csv

# Asteroids and comets.
wget -nc http://ssd.jpl.nasa.gov/dat/ELEMENTS.NUMBR.gz
wget -nc http://ssd.jpl.nasa.gov/dat/ELEMENTS.UNNUM.gz
wget -nc http://ssd.jpl.nasa.gov/dat/ELEMENTS.COMET

# Earth satellites.
wget -nc http://www.celestrak.com/NORAD/elements/visual.txt
