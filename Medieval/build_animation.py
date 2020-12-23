#!/usr/bin/env python3

import argparse
import json
import numpy as np
import sys
from math import cos, sin, tau

BLUE = '#a4dded'
DAYS_PER_SECOND = 72
EARTH_RADIUS_KM = 6378.1366
WIDTH, HEIGHT = 640, 640
planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

SCALE = 50.0
#SCALE = 10.0

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

    styles = []
    svg = []

#     inner = 150.23
#     outer = 987.41
#     svg.append("""
# <circle cx=%(x)d cy=%(y)d r=%(r)d stroke-width=%(w)d stroke=%(blue)s fill=none />
# """ % dict(
#     x=WIDTH//2,
#     y=HEIGHT//2,
#     r=scale((inner + outer) // 2),
#     w=scale(outer - inner),
#     blue='#f8f8e0',
# ))

    for planet_name, params in zip(planets, parameter_sets):
        if len(params) == 4:
            params.extend([1,0,0])
        DT, D0, xe, ye, ET, E0, Er = params
        angle = np.arctan2(ye, xe)
        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        outer_radius = radius * farthest / closest

        deferent_radius = radius / closest
        epicycle_radius = deferent_radius * Er

        km = EARTH_RADIUS_KM
        print(f'{planet_name:8} {eccentricity:5.3f}  '
              f'{radius:9,.1f} - {outer_radius:8,.1f} earth radii  '
              f'{int(radius * km):,} - {int(outer_radius * km):,} km')

        inner = (1 - eccentricity) * deferent_radius
        svg_params = dict(
            blue=BLUE,
            planet_name=planet_name,
            extra='',
            deferent_radius=scale(deferent_radius),
            deferent_inner=scale(inner),
            deferent_tick=
            f'x1={scale(deferent_radius * 0.96) * cos(angle):.1f} '
            f'y1={scale(deferent_radius * 0.96) * sin(angle):.1f} '
            f'x2={scale(deferent_radius * 1.04) * cos(angle):.1f} '
            f'y2={scale(deferent_radius * 1.04) * sin(angle):.1f}',
            epicycle_radius=scale(epicycle_radius),
            x0=scale(-xe * deferent_radius),
            y0=scale(-ye * deferent_radius),
        )

        if planet_name == 'Sun':
            svg_params['extra'] = SUN_SHINE % svg_params

        if Er == 0:
            svg.append(DEFERENT % svg_params)
        else:
            svg.append(DEFERENT_AND_EPICYCLE % svg_params)

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

    styles = '\n '.join(styles)
    body = SVG % dict(
        elements=''.join(svg),
        width=WIDTH,
        height=HEIGHT,
        x=WIDTH//2,
        y=WIDTH//2,
    )
    content = HTML % dict(
        blue=BLUE,
        body=body,
        styles=styles,
    )
    with open('animation-ptolemy-sidereal.html', 'w') as f:
        f.write(content)

HTML = """<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
 circle, line {
  fill: none;
  stroke: %(blue)s;
  stroke-width: 1.5px;
 }
 circle.planet {
  fill: #000;
  stroke: none;
 }
 circle.sunshine {
  fill: url('#sun-gradient');
  stroke: none;
 }
 .inside {
  border: 5px dotted black;
  stroke-dasharray: 2,2;
 }
 .rotating {
  animation-iteration-count: infinite;
  animation-timing-function: linear;
 }
 %(styles)s
</style></head>
<body>%(body)s</body></html>
"""

SVG = """\
<svg version="1.1" width=%(width)s height=%(height)s>
<defs>
 <radialGradient id="sun-gradient">
  <stop offset=0%% stop-color=#440 />
  <stop offset=10%% stop-color=gold />
  <stop offset=100%% stop-color=#ff00 />
 </radialGradient>
</defs>
<g transform="translate(%(x)s, %(y)s)">
%(elements)s</g></svg>
"""

DEFERENT = """
 <circle class=inside cx=0 cy=0 r=%(deferent_inner)s />
 <g transform="translate(%(x0)s, %(y0)s)">
  <circle cx=0 cy=0 r=%(deferent_radius)s />
  <line %(deferent_tick)s />
  <g class="rotating %(planet_name)s-deferent">
   <g transform="translate(%(deferent_radius)s, 0)">
     <circle class=planet cx=0 cy=0 r=2 />%(extra)s
   </g>
  </g>
 </g>
"""

DEFERENT_AND_EPICYCLE = """
 <circle class=inside cx=0 cy=0 r=%(deferent_inner)s />
 <g transform="translate(%(x0)s, %(y0)s)">
  <circle cx=0 cy=0 r=%(deferent_radius)s />
  <line %(deferent_tick)s />
  <g class="rotating %(planet_name)s-deferent">
   <circle cx=%(deferent_radius)s cy=0 r=%(epicycle_radius)s />
   <g transform="translate(%(deferent_radius)s, 0)">
    <g class="rotating %(planet_name)s-epicycle">
     <line x1=0 y1=0 x2=%(epicycle_radius)s y2=0 />
     <circle class=planet cx=%(epicycle_radius)s cy=0 r=2 />%(extra)s
    </g>
   </g>
  </g>
 </g>
"""

SUN_SHINE = """\
   <circle class=sunshine cx=0 cy=0 r=24 />
"""

if __name__ == '__main__':
    main(sys.argv[1:])
