"""Convert stellar spectral classes to RGB values."""

from numpy import array

def without_v(s):
    return s.replace('(V)', '')

def without_parens(s):
    return s.replace('(', '').replace(')', '')

def build_color_chart(path):
    chart = {}

    with open(path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.split()
            spectral_class = fields[0]
            rgb = array([ float(field) / 255.0 for field in fields[3:6] ])
            chart[spectral_class] = rgb
            chart[without_v(spectral_class)] = rgb
            chart[without_parens(spectral_class)] = rgb

    return chart
