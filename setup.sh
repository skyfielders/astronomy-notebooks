#!/bin/bash

set -e
cd $(dirname "${BASH_SOURCE[0]}")
virtualenv venv
source venv/bin/activate

pip install ipython
pip install tornado
pip install pyzmq

pip install pyephem
