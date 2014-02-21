import json
from IPython.display import HTML
from collections import defaultdict
from gzip import GzipFile

def parse_hipparcos(lines):
    for line in lines:
        s = line[41:46].strip()
        if not s:
            continue
        magnitude = float(s)
        if magnitude > 5.0:
            continue
        s = line[51:63].strip()
        if not s:
            continue
        ra = float(s)
        dec = float(line[64:76])
        s = line[245:251].strip()
        if not s:
            continue
        bv = float(s)
        yield ra, dec, magnitude, bv

def group_stars_by_magnitude(records):
    magnitude_groups = defaultdict(list)
    for ra, dec, magnitude, bv in records:
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
    boundaries = defaultdict(list)

    with open('data/bound_18.dat') as f:
        for line in f:
            ra, dec, con, o = line.split()
            boundaries[con].append([float(ra) * -15.0, float(dec)])

    return {con: {"type": "Polygon",
                  "coordinates": [list(improve_boundary(con,boundary))]}
            for con, boundary in sorted(boundaries.items())}

def improve_boundary(con,boundary):
    """Build a constellation boundary.

    East-to-west constellation boundary lines, unless they lie along the
    equator at declination zero, are not great circles and cannot simply
    be rendered using their two endpoints.  Instead, they have to be
    approximated by a series of points.

    This routine also fixes the fact that the input boundaries have an
    implied final segment back to their starting point, which d3 will
    need actually duplicated at the end of the list.

    """
    boundary = boundary + boundary[0:1]
    for (ra0, dec0), (ra1, dec1) in zip(boundary[:-1], boundary[1:]):
        yield ra0, dec0
        is_great_circle = (ra0 == ra1) or (dec0 == dec1 == 0.0)
        if is_great_circle:
            continue
        assert dec0 == dec1
        ra = ra0
        step = direction(ra, ra1)
        ra += step
        while direction(ra, ra1) == step:
            yield ra, dec0
            ra += step
    yield ra1, dec1
    yield boundary[0]

def direction(ra0, ra1):
    """Step direction in which `ra1` can be reached most quickly from `ra0`."""
    return +1.0 if (ra1 - ra0) % 360.0 < 180.0 else -1.0

def load_decision_data():
    with open('data/data.dat') as f:
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
    with open('sky.js') as f:
        js_code = f.read()

    with open('sky.html') as f:
        html_template = f.read()

    html = html_template % {
        'boundary_data': jsonify(build_boundary_data()),
        'decision_data': jsonify(list(load_decision_data())),
        'star_data': jsonify(build_star_data()),
        'js_code': js_code,
        }
    html = html.replace('UNIQUE_ID', 'abcd')
    return HTML(html)
