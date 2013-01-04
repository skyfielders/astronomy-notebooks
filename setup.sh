#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")

if [ ! -d venv ]
then
    virtualenv --system-site-packages venv
    source venv/bin/activate

    pip install basemap
    pip install ipython
    pip install mayavi
    # pip install pandas
    # pip install tables
    pip install tornado
    pip install pyzmq

    pip install pyephem

    mkdir -p data
fi

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
