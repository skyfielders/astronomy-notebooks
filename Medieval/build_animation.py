#!/usr/bin/env python3

import argparse
import json
import numpy as np
import sys
from fitting import equant, to_longitude
from math import cos, sin, tau
from scipy.optimize import curve_fit

BLUE = '#a4dded'  # "Non-photo blue"
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
        #return f'{n / SCALE:.1f}'
        return round(n / SCALE, 1)
        #return int(n / SCALE)

    def scale_days(days):
        return days / DAYS_PER_SECOND

    styles = []
    svg = []

    for planet_name, params in zip(planets, parameter_sets):
        if len(params) == 4:
            params.extend([1,0,0])
        DT, D0, xe, ye, ET, E0, Er = params
        #ye *= -1  # The y coordinate increases down in SVG.

        perigee_angle = np.arctan2(ye, xe) / tau * 360
        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        outer_radius = radius * farthest / closest

        deferent_radius = radius / closest
        epicycle_radius = scale(deferent_radius * Er)

        km = EARTH_RADIUS_KM
        print(f'{planet_name:8} {eccentricity:5.3f}  '
              f'{radius:9,.1f} - {outer_radius:8,.1f} earth radii  '
              f'{int(radius * km):,} - {int(outer_radius * km):,} km')

        inner = (1 - eccentricity) * deferent_radius

        xp = - inner * xe / eccentricity  # "p": perigee
        yp = - inner * ye / eccentricity

        deferent_tick= (
            f'x1={scale(xp * 0.96)} '
            f'y1={scale(yp * 0.96)} '
            f'x2={scale(xp * 1.04)} '
            f'y2={scale(yp * 1.04)}'
        )

        xp = scale(xp)
        yp = scale(yp)
        x0 = scale(xe * deferent_radius)
        y0 = scale(ye * deferent_radius)
        r = scale(deferent_radius)

        extra = ''
        if planet_name == 'Sun':
            extra = '<circle class=sunshine cx=0 cy=0 r=24 />'
        elif Er:
            extra = f"""<circle cx=0 cy=0 r={epicycle_radius} />
     <g class="epicycle {planet_name}-epicycle">
      <line x1=0 y1=0 x2={epicycle_radius} y2=0 />
      <circle cx={epicycle_radius} cy=0 r=2 class=planet />{extra}
     </g>\
"""
        else:
            extra = '<circle class=planet cx=0 cy=0 r=2 />'

        # motion_path = (f'M{xp},{yp}'
        #                f' A {r} {r} 0 0 0 {yp} {-xp}'
        #                f' A {r} {r} 0 0 0 {-xp} {-yp}'
        #                f' A {r} {r} 0 0 0 {-yp} {xp}'
        #                f' A {r} {r} 0 0 0 {xp} {yp}')

        svg.append(f"""
 <circle class=inside cx=0 cy=0 r={scale(inner)} />
 <line {deferent_tick} />
 <g transform="translate({x0}, {y0})">
  <circle cx=0 cy=0 r={r} />
  <g class="deferent {planet_name}-fore">
   <g transform="translate({r}, 0)">
    <g class="deferent {planet_name}-back">
     {extra}
    </g>
   </g>
  </g>
 </g>
""")

        styles.append(
            f'.{planet_name}-fore {{'
            f'animation-duration: {scale_days(DT):.2f}s; '
            f'animation-name: {planet_name}-fore'
            '}')
        styles.append(
            f'.{planet_name}-back {{'
            f'animation-duration: {scale_days(DT):.2f}s; '
            f'animation-name: {planet_name}-back'
            '}')

        styles.append(
            f'@keyframes {planet_name}-fore {{'
            f'from {{transform: rotate({D0:.2f}deg)}} '
            f'to {{transform: rotate({D0 + 360:.2f}deg)}}'
            '}')
        styles.append(
            f'@keyframes {planet_name}-back {{'
            f'from {{transform: rotate({E0 + 720 - D0:.2f}deg)}} '
            f'to {{transform: rotate({E0 + 360 - D0:.2f}deg)}}'
            '}')

        styles.append(
            f'.{planet_name}-epicycle {{'
            f'animation-duration: {scale_days(ET):.2f}s;'
            '}')

        #  <path d="{motion_path}" />
        #k = build_keyframes(3, eccentricity, D0)
        # k = build_keyframes(3, .99, D0)
        # keyframes = '\n'.join(' '+line for line in k)

        # styles.append(
        #     f'@keyframes {planet_name}-deferent {{\n'
        #     f'{keyframes}\n'
        #     '}')

        radius = outer_radius

    radius_km = int(radius * EARTH_RADIUS_KM)
    outer_km_per_s = radius_km * tau / (24 * 60 * 60)

    print(f'Outer radius (km): {radius_km:,}')
    print(f'Outer speed (km/s): {outer_km_per_s:,.2f}')
    print(f'Outer speed (m/s): {outer_km_per_s * 1e3:,.2f}')
    print(f'Outer speed (c): {outer_km_per_s / 299792.458:,.3f}')

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
        styles='\n '.join(styles),
    )
    with open('animation-ptolemy-sidereal.html', 'w') as f:
        f.write(content)

def build_keyframes(n, eccentricity, offset):
    for i in range(n):
        percent0, percent1 = 100 * i/n, 100 * (i+1)/n
        c = compute_bezier_that_approximates_equant
        lon0, lon1, x1, y1, x2, y2 = c(percent0, percent1, eccentricity)
        yield f'{percent0:.1f}% {{'
        yield f' transform: rotate({offset - lon0:.1f}deg);'
        yield(f' animation-timing-function:'
              f' cubic-bezier({x1:.6f},{y1:.6f},{x2:.6f},{y2:.6f});')
        yield '}'
    yield f'to {{transform: rotate({offset - 360:.1f}deg);}}'

def compute_bezier_that_approximates_equant(percent0, percent1, eccentricity):
    percent = np.linspace(percent0, percent1)
    lon = to_longitude(equant(percent / 100.0 * tau, eccentricity, 0), 0.0)
    lon %= 360.0
    lon0, lon1 = lon[0], lon[-1]
    x = np.linspace(0, 1)
    y = (lon - lon0) / (lon1 - lon0)  # Map longitude to range [0,1]
    (x1, y1, x2, y2), variance = curve_fit(
        bezier_interpolated, x, y,
        [0.5, 0.0, 0.5, 1.0],
        bounds=[0, 1],
    )
    return lon0, lon1, x1, y1, x2, y2

def bezier_interpolated(x, x1, y1, x2, y2):
    """Interpolate the value of the given Bezier curve at position ``x``."""
    t = np.linspace(0, 1)
    xb, yb = bezier(t, x1, y1, x2, y2)
    y = np.interp(x, xb, yb)
    return y

def bezier(t, x1, y1, x2, y2):
    """The famous Bezier curve."""
    m = 1 - t
    p = 3 * m * t
    b, c, d = p * m, p * t, t * t * t
    return (b * x1 + c * x2 + d,
            b * y1 + c * y2 + d)

HTML = """<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
 circle, line, path {
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
  border: 5px dotted %(blue)s;
  stroke-dasharray: 2,2;
 }
 .epicycle, .deferent {animation-iteration-count: infinite;}
 .epicycle {animation-timing-function: linear; animation-name: epicycle;}
 @keyframes epicycle {
  from {transform: rotate(0deg)} to {transform: rotate(360deg)}
 }
 .deferent {animation-timing-function: linear;}
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
<g transform="translate(%(x)s, %(y)s) scale(1, -1)">
%(elements)s</g></svg>
"""

# TODO: Control speed of deferent with something like
# keyTimes="0 ; 1.0" keySplines="0 0.1 0.1 1" calcMode=spline

if __name__ == '__main__':
    main(sys.argv[1:])
