import pandas as pd
from glob import glob

names = glob('wx*')
frames = []
for name in names:
    frames.append(pd.read_csv(name))

d = pd.concat(frames)
d['date'] = d['Time (UTC)'].str[:10]
d['F'] = d['Temperature (degrees F)']
d = d[d['F'] != 200.0]           # 200°F maybe means thermometer is at max?

d = d.groupby('date')['F'].max() # high temperature for each date
d = d.reset_index()              # restore 'date' column

d['date'] = d['date'].str[5:]   # remove year from dates
d = d.groupby('date').mean()

d.to_csv('phantom-ranch-average-high-2018-2022.csv')
