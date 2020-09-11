#!/usr/bin/env python3

import sympy as sy
import matplotlib.pyplot as plt
import numpy as np
from functools import partial
from numpy import arcsin, arctan2, cos, sin, unwrap, sqrt
from scipy.optimize import curve_fit
from skyfield.api import load, tau

def main():
    # solve_equant()
    # return

    # plot_equant()
    # return

    ts = load.timescale()

    #days = 365 * 20
    days = 365 * 4
    t = ts.tt(2010, 1, range(days))

    # t = ts.tt(2010, 1, range(365 * 1))
    # t = ts.tt(2010, 1, range(75, 85))
    # t = ts.tt(2010, 1, 79, range(48))
    #for i, x in enumerate(t.utc_jpl()):
    # for x in t.utc_jpl():
    #     #print(('****' if i == 10 else ''), x)
    #     print(x)

    planets = load('de421.bsp')
    #fit(t, planets, 'sun')
    fit(t, planets, 'mars')

def fit(t, planets, name):

    planet = planets[name]
    # planet = planets['jupiter barycenter']
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

    #ax.plot(t, s, label='label', linestyle='--')

    #equant = equant(T, ω, e)

    #ax.plot(day, lon)
    #ax.plot(day, degrees(equant(day, T, M0, ω, e)) - degrees(lon))
    #ax.plot(day[:-1], dt)

    #print(T, M0, e, ω)

    # (T, M0, xe, ye), covariance = curve_fit(equant, day, lon, (T, M0, ye, ye))
    T, M0, xe, ye = fit_equant(day, longitude)

    print(T, M0, xe, ye)
    print([day[0], day[1], day[2]])
    print(equant_orbit([day[0], day[1], day[2]], T, M0, xe, ye))

    angle = to_longitude(equant_orbit)(day, T, M0, xe, ye)
    residual = angle - longitude

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(day, degrees(longitude))
    ax1.plot(day, degrees(angle))
    ax2.plot(day, degrees(residual))

    if name != 'sun':
        T, M0, xe, ye, Tₑ, E0, r = fit_equant_and_epicycle(
            day, longitude, T, M0, xe, ye,
        )

        print(T, M0, xe, ye, Tₑ, E0, r)

        angle = to_longitude(equant_and_epicycle)(day, T, M0, xe, ye, Tₑ, E0, r)
        ax3.plot(day, degrees(longitude))
        ax3.plot(day, degrees(angle))

        residual = angle - longitude
        ax2.plot(day, degrees(residual))
        ax4.plot(day, degrees(residual))

        # x, y = equant_and_epicycle(day, T, M0, xe, ye, Tₑ, E0, r)
        # ax4.plot(x, y)

    # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    # ax.plot(day, degrees(longitude))
    # ax.plot(day, degrees(angle))

    # ax.plot(day, degrees(equant(day, T, M0, e, ω) + epicycle(day, Tₑ, E0, r)
    #                      - longitude))

    #ax.plot(day, degrees(equant(day, T, ω, -e)) - degrees(lon))
    #ax.plot(day, degrees(equant(day, T, ω-tau/2, -e)+tau/2) - degrees(lon))

    # ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Title')
    # ax.set_aspect(aspect=1.0)
    # ax.grid()
    # plt.legend()
    fig.savefig(f'fit_{name}.png')

def fit_equant(day, longitude):
    days = day[-1] - day[0]
    revolutions = (longitude[-1] - longitude[0]) / tau
    T = days / revolutions
    M0 = longitude[0]
    xe = 0
    ye = 0

    # print(days)
    # print(revolutions)
    def f(t, T, M0): #, xe, ye):
        return equant_orbit(t, T, M0, xe, ye)

    (T, M0, #  xe, ye
    ), covariance = curve_fit(
        to_longitude(f), day, longitude, (T, M0, # xe, ye,
        ))

    # # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    return T, M0, xe, ye

def fit_equant_and_epicycle(day, longitude, T, M0, xe, ye):
    angle = to_longitude(equant_orbit)(day, T, M0, xe, ye)
    residual = longitude - angle
    zeros = (residual < 0)[:-1] & (residual > 0)[1:]
    zero_days = day[:-1][zeros]
    print('========', (zero_days[-1] - zero_days[0]) / (len(zero_days) - 1))

    Tₑ = (zero_days[-1] - zero_days[0]) / (len(zero_days) - 1)
    E0 = M0 - (1.0 - zero_days[0] / Tₑ) * tau
    #E0 = zero_days[0] / Tₑ
    r = 0.1

    def f(t, Tₑ, E0, r):
        return equant_and_epicycle(t, T, M0, xe, ye, Tₑ, E0, r)

    (Tₑ, E0, r), covariance = curve_fit(
        to_longitude(f), day, longitude, (Tₑ, E0, r),
    )

    print(Tₑ, E0, r)

    # def f(t, T, M0, e, ω, Tₑ, E0, r):
    #     return equant(t, T, M0, e, ω) + epicycle(t, Tₑ, E0, r)

    # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    return T, M0, xe, ye, Tₑ, E0, r

def degrees(radians):
    return radians / tau * 360.0

def plot_equant():
    M = np.linspace(0, tau * 50.0 / 60.0, 60)
    x, y = equant(M, 0.5, 0.0)
    # print(M)
    # print(x)
    # print(y)
    # print(1 - x*x - y*y)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_aspect(aspect=1.0)
    ax.grid()
    fig.savefig('equant.png')

def to_longitude(f):
    def wrapper(*args):
        x, y = f(*args)
        return unwrap(arctan2(y, x) % tau)
    return wrapper

def equant_and_epicycle(t, T, M0, xe, ye, Tₑ, E0, r):
    x1, y1 = equant_orbit(t, T, M0, xe, ye)
    x2, y2 = epicycle(t, Tₑ, E0, r)
    return x1 + x2, y1 + y2

def equant_orbit(t, T, M0, xe, ye):
    M = M0 + t / T * tau
    x, y = equant(M, xe, ye)
    return x + xe, y + ye

def equant(M, xe, ye):
    offset = arctan2(ye, xe)
    Mo = M - offset
    e = sqrt(xe*xe + ye*ye)
    a = Mo - arcsin(e * sin(Mo))
    a += offset
    return cos(a), sin(a)

def epicycle(t, Tₑ, E0, r):
    E = E0 + t / Tₑ * tau
    return r * cos(E), r * sin(E)

if __name__ == '__main__':
    main()
