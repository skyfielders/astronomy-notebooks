#!/bin/bash

set -e

if ! conda --version >/dev/null 2>&1
then
    echo
    echo 'Error: Cannot find "conda" command'
    echo '       Please install Anaconda'
    echo '       http://continuum.io/downloads'
    echo
    exit 2
fi

cd $(dirname "${BASH_SOURCE[0]}")

# iPython, and the libraries needed for it to run Notebook.
conda install \
    python=2.7 \
    pip \
    ephem \
    ipython-notebook \
    matplotlib \
    mayavi \
    pandas \
    scipy \
    sympy \


pip install \
    de405 \
    jplephem \
    skyfield \
    sgp4 \


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
