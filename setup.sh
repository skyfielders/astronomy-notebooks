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

# To update, run:
# conda list --export > conda.list

conda install --file conda.list

    # pip \
    # ephem \
    # jupyter \
    # matplotlib \
    # mayavi \
    # pandas \
    # scipy \
    # seaborn \
    # sympy \
    # wxpython \


if [ -d ~/skyfield ]
then pip install -e ~/skyfield
else pip install skyfield
fi

# Get ready to download large data sets.
mkdir -p data
# cd data

# echo
# echo 'Setup successful!'
# echo 'Downloading data...'
# python download_data.py
# echo
