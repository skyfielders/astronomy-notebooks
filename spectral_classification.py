"""Convert stellar spectral classes to RGB values."""

def build_color_chart(path):
    chart = {}

    with open(path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            fields = line.split()
            spectral_class = fields[0]
            rgb = tuple(float(field) / 255.0 for field in fields[3:6])
            chart[spectral_class] = rgb

    return chart
