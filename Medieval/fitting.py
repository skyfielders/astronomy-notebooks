#!/usr/bin/env python3

from numpy import arcsin, sin, unwrap
from scipy.optimize import curve_fit
from skyfield.api import load, tau

def main():
    ts = load.timescale()

    days = 365 * 10
    t = ts.tt(2010, 1, range(days))

    # t = ts.tt(2010, 1, range(365 * 1))
    # t = ts.tt(2010, 1, range(75, 85))
    # t = ts.tt(2010, 1, 79, range(48))
    #for i, x in enumerate(t.utc_jpl()):
    # for x in t.utc_jpl():
    #     #print(('****' if i == 10 else ''), x)
    #     print(x)

    planets = load('de421.bsp')
    #planet = planets['sun']
    planet = planets['jupiter barycenter']
    earth = planets['earth']
    #lat, lon, distance = earth.at(t).observe(sun).apparent().ecliptic_latlon()
    lat, lon, distance = earth.at(t).observe(planet).ecliptic_latlon()

    #lon = lon.degrees
    longitude = unwrap(lon.radians)
    # import numpy as np
    # t = np.arange(0.0, 2.0, 0.01)
    # s = 1 + np.sin(2 * np.pi * t)

    day = t.tt - t.tt[0]

    #dt = t.tt[1:] - t.tt[:-1]

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    #ax.plot(t, s, label='label', linestyle='--')

    #equant = equant(T, ω, e)

    #ax.plot(day, lon)
    #ax.plot(day, degrees(equant(day, T, M0, ω, e)) - degrees(lon))
    #ax.plot(day[:-1], dt)

    #print(T, M0, e, ω)

    #(T, M0, e, ω), covariance = curve_fit(equant, day, lon, (T, M0, e, ω))
    T, M0, e, ω = fit_equant(day, longitude)

    # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    print(T, M0, e, ω)
    print('deg', degrees(ω))
    print(e * 60.0)

    ax.plot(day, degrees(equant(day, T, M0, e, ω) - longitude))
    #ax.plot(day, degrees(equant(day, T, ω, -e)) - degrees(lon))
    #ax.plot(day, degrees(equant(day, T, ω-tau/2, -e)+tau/2) - degrees(lon))

    # ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Title')
    # ax.set_aspect(aspect=1.0)
    # ax.grid()
    # plt.legend()
    fig.savefig('tmp.png')

def fit_equant(day, longitude):
    days = day[-1] - day[0]
    revolutions = (longitude[-1] - longitude[0]) / tau
    T = days / revolutions
    M0 = longitude[0]
    e = 0
    ω = 0

    (T, M0, e, ω), covariance = curve_fit(equant, day, longitude, (T, M0, e, ω))

    # Normalize negative e by rotating the orbit 180°.
    if e < 0:
        e = -e
        ω += tau/2
        M0 -= tau/2

    # Normalize ω.
    offset, ω = divmod(ω, tau)
    M0 += offset * tau

    return T, M0, e, ω

def degrees(radians):
    return radians / tau * 360.0

def equant(t, T, M0, e, ω):
    M = M0 + t / T * tau
    return ω + M - arcsin(e * sin(M))

if __name__ == '__main__':
    main()
