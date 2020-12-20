#!/usr/bin/env python3

import argparse
import json
import numpy as np
import os
import sys
from math import tau

DAYS_PER_SECOND = 72
planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

def main(argv):
    parser = argparse.ArgumentParser(description='Write animated SVG.')
    parser.parse_args(argv)

    radius = 59.7  # Ptolemy’s estimate of Moon’s distance in Earth radii
    parameter_sets = []

    for planet_name in planets:
        path = f'parameters_{planet_name}.txt'
        with open(path) as f:
            params = json.load(f)

        print(' '.join(f'{p:9.3f}' for p in params))
        parameter_sets.append(params)

    def scale(n):
        return int(n / 60.0)
        #return int(n / 70.0)

    def scale_days(days):
        return days / DAYS_PER_SECOND

    orbit_parameter_sets = []
    styles = []

    for planet_name, params in zip(planets, parameter_sets):
        DT, D0, xe, ye, ET, E0, Er = params
        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        deferent_radius = radius * 1.0 / closest
        epicycle_radius = deferent_radius * Er
        outer_radius = radius * farthest / closest

        print(f'{path:30} {eccentricity:5.3f}    '
              f'{radius:.2f} - {outer_radius:.2f}')

        orbit_parameter_sets.append(dict(
            deferent_radius=scale(deferent_radius),
            epicycle_radius=scale(epicycle_radius),
            planet_name=planet_name,
            x0=220 + scale(-xe * deferent_radius),
            y0=220 + scale(-ye * deferent_radius),
        ))

        styles.append(
            '.%s-deferent {'
            'animation-duration: %fs;'
            'animation-name: %s-deferent;'
            '}'
            % (planet_name, scale_days(DT), planet_name))
        styles.append(
            '@keyframes %s-deferent {'
            'from {transform: rotate(%ddeg)}'
            'to {transform: rotate(%ddeg)}'
            '}' % (planet_name, int(D0), int(D0) + 360))

        if epicycle_radius:
            print(1 / (1 / ET - 1 / DT))
            styles.append(
                '.%s-epicycle {'
                'animation-duration: %fs;'
                'animation-name: %s-epicycle;'
                '}'
                % (planet_name, scale_days(1 / (1 / ET - 1 / DT)), planet_name))
            styles.append(
                '@keyframes %s-epicycle {'
                'from {transform: rotate(%ddeg)}'
                'to {transform: rotate(%ddeg)}'
                '}' % (planet_name, int(E0 - D0), int(E0 - D0) + 360))

        radius = outer_radius

    earth_radius_km = 6378.1366
    radius_km = int(radius * earth_radius_km)
    outer_km_per_s = radius_km * tau / (24 * 60 * 60)

    print(f'Outer radius (km): {radius_km:,}')
    print(f'Outer speed (km/s): {outer_km_per_s:,.2f}')
    print(f'Outer speed (m/s): {outer_km_per_s * 1e3:,.2f}')
    print(f'Outer speed (c): {outer_km_per_s / 299792.458:,.3f}')

    orbits = '\n'.join(ORBIT % params for params in orbit_parameter_sets)
    styles = '\n '.join(styles)

    x = X % dict(orbits=orbits)
    body = SVG % dict(elements=x)
    content = HTML % dict(body=body, styles=styles)
    with open('animation-ptolemy-sidereal.html', 'w') as f:
        f.write(content)

HTML = """<html>
<style>
.rotating {
 animation-iteration-count: infinite;
 animation-timing-function: linear;
}
 %(styles)s
</style>
<body>%(body)s</body>
</html>"""

SVG = """<svg version=\"1.1\" width=480 height=480>%(elements)s</svg>"""

X = """
 %(orbits)s
"""

ORBIT = """
 <g transform="translate(%(x0)s, %(y0)s)">
  <circle cx=0 cy=0 r=%(deferent_radius)s stroke=#eee fill=none />
  <g class="rotating %(planet_name)s-deferent">
   <circle cx=%(deferent_radius)s cy=0 r=%(epicycle_radius)s stroke=#eee fill=none />
   <g transform="translate(%(deferent_radius)s, 0)">
    <g class="rotating %(planet_name)s-epicycle">
     <line x1=0 y1=0 x2=%(epicycle_radius)s y2=0 stroke=#eee />
     <circle cx=%(epicycle_radius)s cy=0 r=2 fill=#000 />
    </g>
   </g>
  </g>
 </g>
"""

if __name__ == '__main__':
    main(sys.argv[1:])
