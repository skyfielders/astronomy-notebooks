# Quick script to download files.

import datetime as dt

# wxobservations.pl?site=AT680&days=3653
# Resulting CSV has 50,000 data rows.
# Starts 2017-05-01, ends at 2018-01-11 02:25.
# So what would I grab to start over and get all of that date?

# Asking for 1648 days misses a few hours, starting 2018-01-11 4:10.
# I need to ask for 1649 to start at 2018-01-10 04:08 and, at the
# expense of some overlap, catch all of the rows.

#start = dt.date(2018, 1, 11)  # 1649: stops at 2018-09-17 7:43
#start = dt.date(2018, 9, 17)  # 1400: stops at 2019-07-29
#start = dt.date(2019, 7, 29)  # 1085: stops at 2021-01-16
#start = dt.date(2021, 1, 16)  # 548: stops at 2022-05-06
start = dt.date(2022, 5, 6)  # 548: stops at 2022-05-06
today = dt.date.today()

print(today - start)
days = (today - start).days + 1

url = (
    'https://weather.gladstonefamily.net/'
    'cgi-bin/wxobservations.pl'
    '?site=AT680&days={}'.format(days)
)
print(url)

import subprocess
subprocess.check_call(['wget', url])
