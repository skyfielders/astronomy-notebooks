#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")

if [ ! -d venv ]
then
    virtualenv --system-site-packages venv
fi

source venv/bin/activate

#pip install basemap

# iPython, and the libraries needed for it to run Notebook.

pip install ipython
pip install tornado
pip install pyzmq

# Visualization tools and their dependencies.

pip install numpy
pip install scipy
pip install matplotlib
pip install vtk
pip install mayavi
pip install wxPython

# Tools specifically for the 'iPython Features' notebook.

pip install sympy

#pip install networkx

# if [ ! -d profile_default/static/jsplugins/d3 ]
# then
#     git clone https://github.com/ipython/jsplugins.git

#     JSPLUGINS=profile_default/static/jsplugins
#     mkdir -p $JSPLUGINS
#     mv jsplugins/d3/d3 $JSPLUGINS
#     mv jsplugins/d3graph/d3graph $JSPLUGINS
#     mv jsplugins/d3graph/d3graph.py venv/lib/python2.7/site-packages
#     rm -rf jsplugins
# fi

# pip install pandas
# pip install tables

# Astronomical software.

pip install pyephem
pip install jplephem
pip install de405
pip install sgp4

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
