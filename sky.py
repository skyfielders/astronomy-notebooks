import json
from IPython.display import HTML
from collections import defaultdict
from gzip import GzipFile

def parse_hipparcos(lines):
    for line in lines:
        s = line[41:46]
        if s == '     ':
            continue
        magnitude = float(s)
        if magnitude > 5.0:
            continue
        s = line[51:63].strip()
        if not s:
            continue
        ra = float(s)
        dec = float(line[64:76])
        yield ra, dec, magnitude

def group_stars_by_magnitude(records):
    magnitude_groups = defaultdict(list)
    for ra, dec, magnitude in records:
        radec = [-ra, dec]
        magnitude_groups[int(magnitude)].append(radec)
    return magnitude_groups

def starfield():
    with open('sky.js') as f:
        js_code = f.read()

    with GzipFile('/home/brandon/Downloads/hip_main.dat.gz') as f:
        records = parse_hipparcos(f)
        magnitude_groups = group_stars_by_magnitude(records)

    data = [
        {"type": "MultiPoint", "coordinates": coordinates, "magnitude": m}
        for (m, coordinates) in sorted(magnitude_groups.items())
        ]

    js_data = json.dumps(data, separators=(',', ':'))

    html = html_pattern.format(js_code=js_code, js_data=js_data)
    html = html.replace('UNIQUE_ID', 'abcd')
    return HTML(html)

html_pattern = """\
<script>
var star_data = {js_data};
{js_code}
</script>
<div id="UNIQUE_ID"></div>
"""
