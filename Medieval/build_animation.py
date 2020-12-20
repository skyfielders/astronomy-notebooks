#!/usr/bin/env python3

import argparse
import json
import numpy as np
import os
import sys
from math import tau

#planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()
planets = 'Mercury Venus Sun Mars Jupiter Saturn'.split()

def main(argv):
    parser = argparse.ArgumentParser(description='Write animated SVG.')
    parser.parse_args(argv)

    radius = 59.7  # Ptolemy’s estimate of Moon’s distance in Earth radii
    orbit_parameter_sets = []

    def scale(n):
        return int(n / 70.0)

    for planet_name in planets:
        path = f'parameters_{planet_name}.txt'
        with open(path) as f:
            params = json.load(f)

        DT, D0, xe, ye, ET, E0, Er = params
        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        deferent_radius = radius * 1.0 / closest
        outer_radius = radius * farthest / closest

        print(f'{path:30} {eccentricity:5.3f}    '
              f'{radius:.2f} - {outer_radius:.2f}')

        orbit_parameter_sets.append(dict(
            deferent_radius=scale(deferent_radius),
            epicycle_radius=scale(deferent_radius * Er),
            planet_name=planet_name.lower(),
        ))

        radius = outer_radius

    earth_radius_km = 6378.1366
    radius_km = int(radius * earth_radius_km)
    outer_km_per_s = radius_km * tau / (24 * 60 * 60)

    print(f'Outer radius (km): {radius_km:,}')
    print(f'Outer speed (km/s): {outer_km_per_s:,.2f}')
    print(f'Outer speed (m/s): {outer_km_per_s * 1e3:,.2f}')
    print(f'Outer speed (c): {outer_km_per_s / 299792.458:,.3f}')

    orbits = '\n'.join(ORBIT % params for params in orbit_parameter_sets)
    x = X % dict(orbits=orbits)
    body = SVG % dict(elements=x)
    content = HTML % dict(body=body)
    with open('animation-ptolemy-sidereal.html', 'w') as f:
        f.write(content)

HTML = """<html>
<style>
.rotating {
 animation-iteration-count: infinite;
 animation-timing-function: linear;
 animation-name: rotating;
}
.mercury-deferent {
 animation-duration: 10s;
}
.mercury-epicycle {
 animation-duration: 1s;
}
.venus-deferent {
 animation-duration: 10s;
}
.venus-epicycle {
 animation-duration: 1s;
}
@keyframes rotating {to {transform: rotate(360deg);}}
</style>
<body>%(body)s</body>
</html>"""

SVG = """<svg version=\"1.1\" width=480 height=480>%(elements)s</svg>"""

X = """
 %(orbits)s
"""

ORBIT = """
 <g transform="translate(200, 200)">
  <circle cx=0 cy=0 r=%(deferent_radius)s stroke=#eee fill=none />
  <g class="rotating %(planet_name)s-deferent">
   <circle cx=%(deferent_radius)s cy=0 r=%(epicycle_radius)s stroke=#eee fill=none />
   <g transform="translate(%(deferent_radius)s, 0)">
    <g class="rotating %(planet_name)s-epicycle">
     <circle cx=%(epicycle_radius)s cy=0 r=3 fill=#880 />
    </g>
   </g>
  </g>
 </g>
"""

if __name__ == '__main__':
    main(sys.argv[1:])
