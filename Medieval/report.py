#!/usr/bin/env python3

import argparse
import json
import numpy as np
import sys

planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

def main(argv):
    parser = argparse.ArgumentParser(description='Print out eccentricities')
    parser.parse_args(argv)

    radius = 59.7  # Ptolemy’s estimate of Moon’s distance in Earth radii

    for planet_name in planets:
        path = f'parameters_{planet_name}.txt'
        with open(path) as f:
            params = json.load(f)

        if len(params) == 7:
            DT, D0, xe, ye, ET, E0, Er = params
        elif len(params) == 4:
            DT, D0, xe, ye = params
            Er = 0.0

        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        outer_radius = radius * farthest / closest

        print(f'{path:30} {eccentricity:5.3f}    '
              f'{radius:.2f} - {outer_radius:.2f}')

        radius = outer_radius

if __name__ == '__main__':
    main(sys.argv[1:])
