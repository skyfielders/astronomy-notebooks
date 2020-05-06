import os
from urllib.request import urlopen

DATA_SETS = [
    'ftp://cdsarc.u-strasbg.fr/pub/cats/I/239/hip_main.dat.gz',
    'ftp://cdsarc.u-strasbg.fr/pub/cats/VI/42/data.dat',
    'http://ssd.jpl.nasa.gov/dat/ELEMENTS.COMET',
    'http://ssd.jpl.nasa.gov/dat/ELEMENTS.NUMBR.gz',
    'http://ssd.jpl.nasa.gov/dat/ELEMENTS.UNNUM.gz',
    'http://www.celestrak.com/NORAD/elements/visual.txt',
    'http://www.pbarbier.com/constellations/bound_verts_18.txt',
    'https://raw.github.com/astronexus/HYG-Database/master/hygfull.csv',
]

def download_all():
    this_dir = os.path.dirname(__file__)
    original_cwd = os.getcwd()
    os.chdir(this_dir or '.')
    DATA_DIR='data'
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    os.chdir(DATA_DIR)
    for url in DATA_SETS:
        print('Getting data file {0}...'.format(url))
        get_data_set(url)
    print('Done!')
    os.chdir(original_cwd)

def get_data_set(url):
    fname = url.split('/')[-1]
    if os.path.isfile(fname):
        return
    data = urlopen(url).read()
    with open(fname, 'wb') as f:
        f.write(data)
