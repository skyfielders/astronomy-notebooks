import os, requests

DATA_SETS = [
('hygfull.csv', 'https://raw.github.com/astronexus/HYG-Database/master/hygfull.csv'),
('ELEMENTS.NUMBR.gz', 'http://ssd.jpl.nasa.gov/dat/ELEMENTS.NUMBR.gz'),
('ELEMENTS.UNNUM.gz', 'http://ssd.jpl.nasa.gov/dat/ELEMENTS.UNNUM.gz'),
('ELEMENTS.COMET', 'http://ssd.jpl.nasa.gov/dat/ELEMENTS.COMET'),
('visual.txt', 'http://www.celestrak.com/NORAD/elements/visual.txt')]

def get_data_set(fname, url):
    with open(fname, 'wb') as f:
        r = requests.get(url)
        f.write(r.content)

if __name__ == '__main__':
    os.chdir('data')
    for data_name, location in DATA_SETS:
        get_data_set(data_name, location)
