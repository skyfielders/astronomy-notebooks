import json
import os
from IPython.display import HTML
from collections import defaultdict
from gzip import GzipFile
from math import copysign
from pkgutil import get_data

DATA_DIR = os.path.dirname(__file__) + '/../data'
MAGNITUDE_LIMIT = 7.0

def parse_hipparcos(lines):
    """Iterate across the `lines` of ``hip_main.dat`` and yield records."""
    for lineno, line in enumerate(lines):
        #For the description of this format, see See http://cdsarc.u-strasbg.fr/viz-bin/Cat?I/239
        try:
            magnitude = float(line[41:46])
            ra = float(line[51:63])
            dec = float(line[64:76])
            bv = float(line[245:251])
            yield ra, dec, magnitude, bv
        except:
            #print("Unable to parse line #{0}".format(lineno))
            continue

def group_stars_by_magnitude(records):
    magnitude_groups = defaultdict(list)
    for ra, dec, magnitude, bv in records:
        if magnitude > MAGNITUDE_LIMIT:
            continue
        radec = [-ra, dec]
        if bv < 0.00:
            color = 'blue'
        elif bv < 0.59:
            color = 'white'
        else:
            color = 'red'
        key = (int(magnitude), color)
        magnitude_groups[key].append(radec)
    return magnitude_groups

def build_boundary_data():
    """Load constellation boundaries.

    Boundary declination is always an integer number of minutes of arc;
    right ascension, an integral number of seconds of right ascension.
    We therefore represent them using these integers, which can both be
    represented more compactly in the JavaScript we produce, and which
    also remove rounding errors as we compute.

    """
    boundaries = defaultdict(list)

    with open(DATA_DIR + '/bound_verts_18.txt') as f:
        for line in f:
            vertex_key, ra_text, dec_text, con, cons = line.split(' ', 4)
            h, m, s = [int(s) for s in ra_text.split(':')]
            ra = (60 * h + m) * 60 + s
            d, m, s = [int(s) for s in dec_text.split(':')]
            assert s == 0
            m = copysign(m, d)
            dec = 60 * d + m
            boundaries[con].append([ra, dec])

    return {con: {"type": "Polygon", "coordinates": [list(boundary)]}
            for con, boundary in sorted(boundaries.items())}

def load_decision_data():
    with open(DATA_DIR + '/data.dat') as f:
        for line in f:
            ra0, ra1, dec, con = line.split()
            yield float(ra0) * 15.0, float(ra1) * 15.0, float(dec), con.upper()

def build_star_data():
    with GzipFile('data/hip_main.dat.gz') as f:
        records = parse_hipparcos(f)
        magnitude_groups = group_stars_by_magnitude(records)

    return [
        {
            "type": "MultiPoint",
            "coordinates": coordinates,
            "magnitude": mag,
            "color": color,
        }
        for ((mag, color), coordinates) in sorted(magnitude_groups.items())
    ]

def jsonify(data):
    """Render `data` as compact JSON."""
    return json.dumps(data, separators=(',', ':')).replace('"', "'")

def starfield():
    js_code = get_data(__name__, 'sky.js').decode('utf-8')
    html_template = get_data(__name__, 'sky.html').decode('utf-8')

    html = html_template % {
        'boundary_data': jsonify(build_boundary_data()),
        'decision_data': jsonify(list(load_decision_data())),
        'star_data': jsonify(build_star_data()),
        'js_code': js_code,
        }
    html = html.replace('UNIQUE_ID', 'abcd')

    return HTML(html)

if __name__ == '__main__':
    print(build_boundary_data()['CEP']['coordinates'][0])
