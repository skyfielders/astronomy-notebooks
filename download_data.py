import os, urllib2

DATA_SETS = [
    'ftp://cdsarc.u-strasbg.fr/pub/cats/VI/49/bound_18.dat',
    'https://raw.github.com/astronexus/HYG-Database/master/hygfull.csv',
    'http://ssd.jpl.nasa.gov/dat/ELEMENTS.NUMBR.gz',
    'http://ssd.jpl.nasa.gov/dat/ELEMENTS.UNNUM.gz',
    'http://ssd.jpl.nasa.gov/dat/ELEMENTS.COMET',
    'http://www.celestrak.com/NORAD/elements/visual.txt',
    ]

def get_data_set(url):
    fname = url.split('/')[-1]
    if os.path.isfile(fname):
        return
    data = urllib2.urlopen(url).read()
    with open(fname, 'wb') as f:
        f.write(data)

if __name__ == '__main__':
    os.chdir('data')
    for url in DATA_SETS:
        get_data_set(url)
