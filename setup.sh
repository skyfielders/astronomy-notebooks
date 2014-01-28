#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")

if [ ! -d venv ]
then
    virtualenv --system-site-packages venv
fi

debug () { false; }

pip_freeze () {
    if debug; then
        if [ ! -e pip_i ]; then
            echo '0' >pip_i
        fi
        i=`cat pip_i`
        if [ -n "$*" ]; then
            args=`echo "$*" | tr ' ' '-'`
            pip freeze >`printf 'requirements.%02d.%s.txt' "$i" "$args"`
        else
            pip freeze >`printf 'requirements.%02d.txt' "$i"`
        fi
        echo `expr "$i" + 1` >pip_i
    fi
}

pip_install () {
    pip install "$@"
    pip_freeze "$@"
}

pip_freeze 'before activate'
source venv/bin/activate
pip_freeze 'after activate'
pip_install --upgrade distribute

# iPython, and the libraries needed for it to run Notebook.
pip_install ipython
pip_install tornado
pip_install pyzmq
pip_install jinja2

# Visualization tools and their dependencies.
pip_install numpy
pip_install scipy
pip_install matplotlib
pip_install vtk
pip_install mayavi==4.3.0
pip_install traits==4.3.0
pip_install traitsui==4.3.0
pip_install pyface==4.3.0
pip_install wxPython

# Tools specifically for the 'An-Introduction--Notebook-Features' notebook.
pip_install sympy

# Astronomical software.
pip_install pyephem
pip_install jplephem
pip_install de405
pip_install sgp4
pip_install skyfield==0.1

# Tools specifically for the 'An-Introduction--Pandas' notebook.
# pip install pandas # 2014-01-15 0.13.0 crashes, hence following fudge.
pip_install pandas==0.12.0

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
