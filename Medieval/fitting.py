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

    days = 365 * 10
    #days = 365 * 4
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
    #fit(t, planets, 'mars')
    fit2(t, planets, 'mars')

def fit2(t, planets, name):
    planet = planets[name]
    earth = planets['earth']
    lat, lon, distance = earth.at(t).observe(planet).ecliptic_latlon()

    day = t.tt - t.tt[0]
    longitude = degrees(unwrap(lon.radians))

    # Parameters we need:
    # equant_and_epicycle(t, T, M0, xe, ye, Tₑ, E0, r)
    #
    # (new name - descr)
    # y DT - period of deferent
    # y D0 - angular position on orbit at time 0
    #  x, y - position of Earth, relative to center of circular orbit at (0,0)
    # y ET - epicycle period
    #  E0 - angular position of epicycle at time 0
    #  Er - Radius of epicycle, where circular orbit has radius = 1.

    # Let's go after epicycle first, rather than deferent period!

    derivative_sign_diff = np.diff(np.sign(np.diff(longitude)))
    retrograde_starts, = np.nonzero(derivative_sign_diff < 0)
    retrograde_ends, = np.nonzero(derivative_sign_diff > 0)
    if retrograde_ends[0] < retrograde_starts[0]:
        retrograde_ends = retrograde_ends[1:]
    if retrograde_ends[-1] < retrograde_starts[-1]:
        retrograde_starts = retrograde_starts[1:]

    assert len(retrograde_starts) == len(retrograde_ends)

    retrograde_middles = (retrograde_ends + retrograde_starts) / 2.0
    m = retrograde_middles.astype(int)
    print(retrograde_starts)
    print(retrograde_ends)
    print(retrograde_middles)
    print(m)

    days = m[-1] - m[0]
    epicycle_orbits = len(m) - 1
    deferent_orbits = (longitude[m[-1]] - longitude[m[0]]) / 360.0

    DT = days / deferent_orbits
    print('DT:', DT)

    D0 = longitude[m[0]] - 360.0 * m[0] / DT
    print('D0:', D0)

    ET = days / (deferent_orbits + epicycle_orbits)
    #ET = DT - days / epicycle_orbits
    print('ET:', ET)

    # at time m[0], epicycle had angle: -longitude[m[0]]
    # and its period is ET
    # so its angle at time 0 must be: -longitude[m[0]] - 360.0 * m[0]
    # (Why the 180°?)
    E0 = (longitude[m[0]] - 360.0 * (m[0] / ET) - 180.0)

    # equant_and_epicycle(t, T, M0, xe, ye, Tₑ, E0, r)
    # (T, M0, xe, ye), covariance = curve_fit(equant, day, lon, (T, M0, ye, ye))

    # def f(day, r):
    #     return to_longitude(equant_and_epicycle(day, DT, D0, 0, 0, ET, E0, r))

    # [r], etc = curve_fit(f, day, longitude, p0=[0.5])
    # print(r)

    params = np.array([DT, D0, 0, 0, ET, E0, 0.5])

    fig, axes = plt.subplots(len(params), 1)
    # y = to_longitude(equant_and_epicycle(day, DT, D0, 0, 0, ET, E0, r))
    # print(day.shape)
    # print(y.shape)
    # ax.plot(day, longitude)
    #ax.plot(day, y)

    def sum_of_squares(t, *params):
        print('t', t.shape)
        for i, v in enumerate(params):
            print(i, v.shape)
        y = to_longitude(equant_and_epicycle(t, *params))
        print('y', y.shape)  # (3650, 100)
        i = 50
        # ax1.plot(t[:,0], y[:,i])
        # ax1.plot(t[:,0], longitude)
        delta = (y - longitude[:,None])
        return (delta * delta).sum(axis=0)

    N = 1000
    span = np.linspace(-1.0, 1.0, N) #[None,:]
    #span = np.linspace(-0.30, 0.30, N) #[None,:]
    zero = span * 0.0
    one = span + 1.0
    print(span.shape, zero.shape, one.shape) # (1,100) all
    #y = to_longitude(equant_and_epicycle(day, DT, D0, 0, 0, ET, E0, r))

    scales = [10.0, 10.0, 0.3, 0.3, 10.0, 10.0, 0.3]
    assert len(scales) == len(params)

    for i, scale in enumerate(scales):
        print(':', params.shape, zero.shape) # TODO
        param_arrays = params[:,None] + zero  # (7,N)
        print(':pa', param_arrays.shape)
        print(':', param_arrays[i].shape)  #(N)
        param_arrays[i] += span * scale
        this_param = param_arrays[i]
        #r = 0.5 + span * 0.45
        sq = sum_of_squares(day[:,None], *param_arrays)
        print('::', this_param.shape) # (N)
        print('::', sq.shape) # (N)
        axes[i].plot(this_param, sq, '.')

    fig.savefig(f'fit_{name}.png')

    def f(day, DT, D0, xe, ye, ET, E0, r):
        return to_longitude(equant_and_epicycle(day, DT, D0, xe, ye, ET, E0, r))

    params, etc = curve_fit(f, day, longitude, p0=params)
    print(params)

    fig, ax = plt.subplots(1,1)
    ax.plot(day, longitude)
    ax.plot(day, to_longitude(equant_and_epicycle(day, *params)))
    fig.savefig(f'fit2_{name}.png')

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

def to_longitude(xy):
    x, y = xy
    return unwrap(arctan2(y, x), axis=0) / tau * 360.0

def to_radians(degrees):
    return degrees / 360.0 * tau

def equant_and_epicycle(t, T, M0, xe, ye, Tₑ, E0, r):
    x1, y1 = equant_orbit(t, T, M0, xe, ye)
    x2, y2 = epicycle(t, Tₑ, E0, r)
    return x1 + x2, y1 + y2

def equant_orbit(t, T, M0, xe, ye):
    M = to_radians(M0) + t / T * tau
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
    E = to_radians(E0) + t / Tₑ * tau
    return r * cos(E), r * sin(E)

if __name__ == '__main__':
    main()
