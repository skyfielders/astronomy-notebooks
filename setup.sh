#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")

if [ ! -d venv ]
then
    virtualenv --system-site-packages venv
fi

source venv/bin/activate
pip install --upgrade distribute

# iPython, and the libraries needed for it to run Notebook.
pip install ipython
pip install tornado
pip install pyzmq
pip install jinja2

# Visualization tools and their dependencies.
pip install numpy
pip install scipy
pip install matplotlib
pip install vtk
pip install mayavi
pip install wxPython

# Tools specifically for the 'An-Introduction--Notebook-Features' notebook.
pip install sympy

# Astronomical software.
pip install pyephem
pip install jplephem
pip install de405
pip install sgp4
git clone https://github.com/brandon-rhodes/python-skyfield.git
pip install ./python-skyfield

# Tools specifically for the 'An-Introduction--Pandas' notebook.
# pip install pandas # 2014-01-15 0.13.0 crashes, hence following fudge.
pip install pandas==0.12.0

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
