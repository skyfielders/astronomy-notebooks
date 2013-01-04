#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")
virtualenv --system-site-packages venv
source venv/bin/activate

pip install basemap
pip install ipython
pip install mayavi
pip install tornado
pip install pyzmq

pip install pyephem

mkdir -p data
cd data

# As described on the http://www.astronexus.com/node/34 page, the
# following link is a star catalog now hosted on github.  HOW COOL!

wget -O hygfull.csv -c \
  https://github.com/astronexus/HYG-Database/blob/master/hygfull.csv?raw=true

# Asteroids and comets.

wget -c http://ssd.jpl.nasa.gov/dat/ELEMENTS.NUMBR.gz
wget -c http://ssd.jpl.nasa.gov/dat/ELEMENTS.UNNUM.gz
wget -c http://ssd.jpl.nasa.gov/dat/ELEMENTS.COMET
