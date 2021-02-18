#!/usr/bin/env python3

import argparse
import json
import numpy as np
import sys
from math import tau
from scipy.optimize import curve_fit

from orbit_math import equant, to_longitude, to_radians

BLUE = '#a4dded'  # "Non-photo blue"
DAYS_PER_SECOND = 72
EARTH_RADIUS_KM = 6378.1366
WIDTH, HEIGHT = 640, 640
MOON_ORBIT_RADIUS = 59.7  # Ptolemy’s estimate of Moon distance, in Earth radii

planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

def main(argv):
    parser = argparse.ArgumentParser(description='Write animated SVG.')
    parser.parse_args(argv)

    parameter_sets = []

    for planet_name in planets:
        path = f'parameters_{planet_name}.txt'
        with open(path) as f:
            params = json.load(f)

        print(' '.join(f'{p:9.3f}' for p in params))
        parameter_sets.append(params)

    with open('texts.html') as f:
        texts = f.read()

    texts = ['<h1>' + text for text in texts.split('<h1>')[1:]]
    names = ['index.html', 'inner-planets.html', 'notes.html']

    for name, text in zip(names, texts):
        if name != 'notes.html':
            scale_factor = 5.0 if 'inner' in name else 50.0
            text = render(scale_factor, parameter_sets, text)
        with open(name, 'w') as f:
            f.write(text)

def render(scale_factor, parameter_sets, text):
    def scale(n):
        return round(n / scale_factor, 1)

    def scale_days(days):
        return round(days / DAYS_PER_SECOND, 2)

    styles = []
    defs = []
    svg_preamble = []
    svg = []

    radius = MOON_ORBIT_RADIUS

    for planet_name, params in zip(planets, parameter_sets):
        if len(params) == 4:
            params.extend([1,0,0])

        DT, D0, xe, ye, ET, E0, Er = params
        eccentricity = np.sqrt(xe * xe + ye * ye)

        closest = 1.0 - eccentricity - Er
        farthest = 1.0 + eccentricity + Er
        outer_radius = radius * farthest / closest

        deferent_radius = radius / closest
        epicycle_radius = deferent_radius * Er

        km = EARTH_RADIUS_KM
        print(f'{planet_name:7} {eccentricity:5.3f}  '
              f'{radius:8,.1f}-{outer_radius:8,.1f} earth radii  '
              f'{int(outer_radius * km):11,} km', end='  ')

        inner = (1 - eccentricity) * deferent_radius

        x = WIDTH // 2 + scale(xe * deferent_radius)
        y = HEIGHT // 2 - scale(ye * deferent_radius + deferent_radius)
        # text = f'<text x={x} y={y} text-anchor=middle>{planet_name}</text>'
        # svg_preamble.append(text)

        dy = 4
        y1 = HEIGHT // 2 - scale(ye * deferent_radius + deferent_radius) - dy
        y2 = HEIGHT // 2 - scale(ye * deferent_radius - deferent_radius) + dy
        r = scale(deferent_radius) + dy

        x, y1, y2, r = round(x,2), round(y1,2), round(y2,2), round(r,2)

        if r > 30:
            defs.append(
                f'<path id={planet_name}-path'
                f' d="M{x},{y1} A {r} {r} 0 1 1 {x},{y2}" />'
            )

            svg_preamble.append(
                f'<text><textPath href="#{planet_name}-path">'
                f'{planet_name.upper()}</textPath></text>\n'
                #f'{planet_name.upper()}     105×10⁶ km</textPath></text>\n'
            )

        xp = - inner * xe / eccentricity  # "p": perigee
        yp = - inner * ye / eccentricity

        deferent_tick= (
            f'x1={scale(xp * 0.96)} '
            f'y1={scale(yp * 0.96)} '
            f'x2={scale(xp * 1.04)} '
            f'y2={scale(yp * 1.04)}'
        )

        x = scale(xe * deferent_radius)
        y = scale(ye * deferent_radius)
        r = scale(deferent_radius)
        e = scale(epicycle_radius)

        extra = ''
        if planet_name == 'Sun':
            extra = f'   <circle class=sunshine cx={r} cy=0 r=24 />'
        elif Er:
            extra = f"""\
   <g transform="translate({r}, 0) scale(-1, 1)">
    <g class="deferent {planet_name}-deferent">
     <g transform="scale(-1, 1) rotate({E0 % 360:.2f})">
      <circle cx=0 cy=0 r={e} />
      <g class="epicycle {planet_name}-epicycle">
       <line x1=0 y1=0 x2={e} y2=0 />
       <circle cx={e} cy=0 r=2 class=planet />{extra}
      </g>
     </g>
    </g>
   </g>\
"""
        else:
            extra = f'   <circle class=planet cx={r} cy=0 r=2 />'

        svg.append(f"""
 <circle class=inside cx=0 cy=0 r={scale(inner)} />
 <line {deferent_tick} />
 <g transform="translate({x}, {y})">
  <circle cx=0 cy=0 r={r} />
  <g class="deferent {planet_name}-deferent">
{extra}
  </g>
 </g>
""")

        styles.append(
            f'.{planet_name}-deferent {{'
            f'animation-duration: {scale_days(DT)}s; '
            f'animation-name: {planet_name}-deferent'
            '}')

        k = build_keyframes(2, D0, xe, ye)
        keyframes = '\n'.join('  '+line for line in k)

        styles.append(
            f'@keyframes {planet_name}-deferent {{\n'
            f'{keyframes}\n'
            ' }')

        styles.append(
            f'.{planet_name}-epicycle {{'
            f'animation-duration: {scale_days(ET)}s;'
            '}')

        radius = outer_radius

    radius_km = int(radius * EARTH_RADIUS_KM)
    outer_km_per_s = radius_km * tau / (24 * 60 * 60)

    print(f'Outer radius (km): {radius_km:,}')
    print(f'Outer speed (km/s): {outer_km_per_s:,.2f}')
    print(f'Outer speed (m/s): {outer_km_per_s * 1e3:,.2f}')
    print(f'Outer speed (c): {outer_km_per_s / 299792.458:,.3f}')

    svg = SVG % dict(
        defs='\n '.join(defs),
        preamble=''.join(svg_preamble),
        elements=''.join(svg),
        width=WIDTH,
        height=HEIGHT,
        x=WIDTH//2,
        y=HEIGHT//2,
    )
    content = HTML % dict(
        blue=BLUE,
        svg=svg,
        styles='\n '.join(styles),
        text=text,
    )
    return content

def build_keyframes(n, D0, xe, ye):
    very_worst = 0
    for i in range(n):
        fraction0, fraction1 = i/n, (i+1)/n
        M = D0 + 360 * np.linspace(fraction0, fraction1)
        longitude = to_longitude(equant(to_radians(M), xe, ye), M[0])
        x1, y1, x2, y2, worst = fit_bezier(longitude)
        very_worst = max(worst, very_worst)
        yield f'{fraction0 * 100:.1f}% {{'
        yield f' transform: rotate({longitude[0]:.1f}deg);'
        yield(f' animation-timing-function:'
              f' cubic-bezier({x1:.6f},{y1:.6f},{x2:.6f},{y2:.6f});')
        yield '}'
    yield f'to {{transform: rotate({longitude[-1]:.1f}deg);}}'
    print(f'Fit: {very_worst:.4f}°')  # Worst fit, in degrees

def fit_bezier(longitude):
    lon0, lonN = longitude[0], longitude[-1]
    x = np.linspace(0, 1)
    y = (longitude - lon0) / (lonN - lon0)  # Map longitude to range [0,1]
    (x1, y1, x2, y2), variance = curve_fit(
        bezier_interpolated, x, y,
        [0.5, 0.0, 0.5, 1.0], bounds=[0, 1],
    )
    worst = max(abs(bezier_interpolated(x, x1,y1,x2,y2) - y)) * (lonN - lon0)
    return x1, y1, x2, y2, worst

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
 circle.inside {
  border: 5px dotted %(blue)s;
  stroke-dasharray: 2,2;
 }
 text {
  font-family: sans-serif;
  fill: %(blue)s;
 }
 .epicycle, .deferent {animation-iteration-count: infinite;}
 .epicycle {animation-timing-function: linear; animation-name: epicycle;}
 @keyframes epicycle {
  from {transform: rotate(0deg)} to {transform: rotate(360deg)}
 }
 .deferent {animation-timing-function: linear;}
 %(styles)s
</style></head>
<body>%(text)s%(svg)s</body></html>
"""

SVG = """\
<svg version="1.1" width=%(width)s height=%(height)s>
<defs>
 <radialGradient id="sun-gradient">
  <stop offset=0%% stop-color=#440 />
  <stop offset=10%% stop-color=gold />
  <stop offset=100%% stop-color=#ff00 />
 </radialGradient>
 %(defs)s
</defs>
%(preamble)s
<g transform="translate(%(x)s, %(y)s) scale(1, -1)">
%(elements)s</g></svg>
"""

if __name__ == '__main__':
    main(sys.argv[1:])
