#!/usr/bin/env python3

import argparse
import json
import numpy as np
import sys
from math import tau

DAYS_PER_SECOND = 72
EARTH_RADIUS_KM = 6378.1366
WIDTH, HEIGHT = 640, 640
planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

#SCALE = 45.0
SCALE = 10.0

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
        return int(n / SCALE)

    def scale_days(days):
        return days / DAYS_PER_SECOND

    orbit_parameter_sets = []
    styles = []

    for planet_name, params in zip(planets, parameter_sets):
        if len(params) == 4:
            params.extend([1,0,0])
        DT, D0, xe, ye, ET, E0, Er = params
        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        deferent_radius = radius * 1.0 / closest
        epicycle_radius = deferent_radius * Er
        outer_radius = radius * farthest / closest

        km = EARTH_RADIUS_KM
        print(f'{planet_name:10} {eccentricity:5.3f}   '
              f'{radius:9,.2f} - {outer_radius:9,.2f}   '
              f'{int(radius * km):,} - {int(outer_radius * km):,} km')

        svg_params = dict(
            blue='#a4dded',
            planet_name=planet_name,
            extra='',
            deferent_radius=scale(deferent_radius),
            epicycle_radius=scale(epicycle_radius),
            x0=WIDTH // 2 + scale(-xe * deferent_radius),
            y0=HEIGHT // 2 + scale(-ye * deferent_radius),
        )

        # if planet_name in ('Sun', 'Venus', 'Mercury'):
        #     svg_params['extra'] = SUN_LINE % svg_params

        orbit_parameter_sets.append(svg_params)

        styles.append(
            '.%s-deferent {'
            'animation-duration: %fs;'
            'animation-name: %s-deferent;'
            '}'
            % (planet_name, scale_days(DT), planet_name))
        styles.append(
            '@keyframes %s-deferent {'
            'from {transform: rotate(%.2fdeg)}'
            'to {transform: rotate(%.2fdeg)}'
            '}' % (planet_name, D0 + 360, D0))

        if Er > 0:
            styles.append(
                '.%s-epicycle {'
                'animation-duration: %fs;'
                'animation-name: %s-epicycle;'
                '}'
                % (planet_name, scale_days(1 / (1 / ET - 1 / DT)), planet_name))
            styles.append(
                '@keyframes %s-epicycle {'
                'from {transform: rotate(%.2fdeg)}'
                'to {transform: rotate(%.2fdeg)}'
                '}' % (planet_name, E0 - D0 + 360, E0 - D0))

        radius = outer_radius

    radius_km = int(radius * EARTH_RADIUS_KM)
    outer_km_per_s = radius_km * tau / (24 * 60 * 60)

    print(f'Outer radius (km): {radius_km:,}')
    print(f'Outer speed (km/s): {outer_km_per_s:,.2f}')
    print(f'Outer speed (m/s): {outer_km_per_s * 1e3:,.2f}')
    print(f'Outer speed (c): {outer_km_per_s / 299792.458:,.3f}')

    orbits = ''.join(ORBIT % params for params in orbit_parameter_sets)
    styles = '\n '.join(styles)

    x = X % dict(orbits=orbits)
    body = SVG % dict(elements=x, width=WIDTH, height=HEIGHT)
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
<body>%(body)s</body></html>
"""

SVG = ("""<svg version="1.1" width=%(width)s height=%(height)s>"""
       '%(elements)s</svg>')

X = """
 %(orbits)s
"""

ORBIT = """
 <g transform="translate(%(x0)s, %(y0)s)">
  <circle cx=0 cy=0 r=%(deferent_radius)s stroke=%(blue)s fill=none />
  <g class="rotating %(planet_name)s-deferent">%(extra)s
   <circle cx=%(deferent_radius)s cy=0 r=%(epicycle_radius)s stroke=%(blue)s fill=none />
   <g transform="translate(%(deferent_radius)s, 0)">
    <g class="rotating %(planet_name)s-epicycle">
     <line x1=0 y1=0 x2=%(epicycle_radius)s y2=0 stroke=%(blue)s />
     <circle cx=%(epicycle_radius)s cy=0 r=2 fill=#000 />
    </g>
   </g>
  </g>
 </g>
"""
SUN_LINE = """\
   <line x1=0 y1=0 x2=%(deferent_radius)s y2=0 stroke=%(blue)s />
"""


if __name__ == '__main__':
    main(sys.argv[1:])
