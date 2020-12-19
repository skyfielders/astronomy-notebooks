#!/usr/bin/env python3

import argparse
import json
import numpy as np
import os
import sys
from glob import glob

def main(argv):
    parser = argparse.ArgumentParser(description='Print out eccentricities')
    parser.parse_args(argv)

    paths = glob('parameters_*.txt')
    for path in sorted(paths):
        with open(path) as f:
            params = json.load(f)

        DT, D0, xe, ye, ET, E0, Er = params
        eccentricity = np.sqrt(xe * xe + ye * ye)
        print(f'{path:30} {eccentricity:5.3f}')

if __name__ == '__main__':
    main(sys.argv[1:])
