#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys
from numpy import arcsin, arctan2, cos, sin, unwrap, sqrt
from scipy.optimize import curve_fit
from skyfield.api import load, tau

planets = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

def main():
    ts = load.timescale()
    days = 365 * 10
    t = ts.tt(2010, 1, range(days))

    ephemeris = load('de421.bsp')
    planet_name = sys.argv[1]
    target_name = planet_name
    try:
        ephemeris[target_name]
    except KeyError:
        target_name += ' barycenter'

    day = t.tt - t.tt[0]

    planet = ephemeris[target_name]
    earth = ephemeris['Earth']
    lat, lon, distance = earth.at(t).observe(planet).ecliptic_latlon()
    longitude = to_degrees(unwrap(lon.radians))

    if planet_name in ('Moon', 'Sun'):
        initial_params, fitted_params = fit1(day, longitude)
    else:
        initial_params, fitted_params = fit2(day, longitude)

    with open(f'parameters_{planet_name}.txt', 'w') as f:
        print(list(fitted_params), file=f)

    # print('Generating plots')
    # plot_slopes(planet_name, day, longitude, initial_params, fitted_params)
    # plot_solution(planet_name, day, longitude, initial_params, fitted_params)
    # print('Done')

def generate_initial_params(day, longitude):
    derivative_sign_diff = np.diff(np.sign(np.diff(longitude)))
    retrograde_starts, = np.nonzero(derivative_sign_diff < 0)

    if not len(retrograde_starts):
        # No retrograde motion: turn epicycle off.

        days = day[-1] - day[0]
        revolutions = (longitude[-1] - longitude[0]) / 360.0

        D0 = longitude[0]
        DT = days / revolutions

        initial_params = np.array([DT, D0, 0, 0])

    else:
        # Carefully measure deferent using middle of each retrograde swing.

        retrograde_ends, = np.nonzero(derivative_sign_diff > 0)
        if retrograde_ends[0] < retrograde_starts[0]:
            retrograde_ends = retrograde_ends[1:]
        if retrograde_ends[-1] < retrograde_starts[-1]:
            retrograde_starts = retrograde_starts[1:]

        assert len(retrograde_starts) == len(retrograde_ends)

        retrograde_middles = (retrograde_ends + retrograde_starts) / 2.0
        print(retrograde_starts)
        print(retrograde_ends)
        print(retrograde_middles)
        m = retrograde_middles.astype(int)
        print(m)

        days = m[-1] - m[0]
        epicycle_orbits = len(m) - 1
        deferent_orbits = (longitude[m[-1]] - longitude[m[0]]) / 360.0

        DT = days / deferent_orbits
        print('DT:', DT)

        D0 = longitude[m[0]] - 360.0 * m[0] / DT
        print('D0:', D0)

        ET = days / (deferent_orbits + epicycle_orbits)
        print('ET:', ET)

        # (Why the 180°?)
        E0 = (longitude[m[0]] - 360.0 * (m[0] / ET) - 180.0)

        initial_params = np.array([DT, D0, 0, 0, ET, E0, 0.5])

    return initial_params

def fit1(day, longitude):
    initial_params = generate_initial_params(day, longitude)
    null_epicycle = [1.0, 0, 0]

    def f(day, DT, D0, xe, ye):
        xy = equant_and_epicycle(day, DT, D0, xe, ye, *null_epicycle)
        return to_longitude(xy, D0)

    fitted_params, etc = curve_fit(f, day, longitude, p0=initial_params)

    initial_params = np.concatenate([initial_params, null_epicycle])
    fitted_params = np.concatenate([fitted_params, null_epicycle])

    return initial_params, fitted_params

def fit2(day, longitude):

    # Parameters we need:
    # equant_and_epicycle(t, T, M0, xe, ye, Tₑ, E0, Er)
    #
    # (new name - descr)
    # y DT - period of deferent
    # y D0 - angular position on orbit at time 0
    #  x, y - position of Earth, relative to center of circular orbit at (0,0)
    # y ET - epicycle period
    #  E0 - angular position of epicycle at time 0
    #  Er - Radius of epicycle, where circular orbit has radius = 1.

    initial_params = generate_initial_params(day, longitude)

    def f(day, DT, D0, xe, ye, ET, E0, Er):
        xy = equant_and_epicycle(day, DT, D0, xe, ye, ET, E0, Er)
        return to_longitude(xy, D0)

    fitted_params, etc = curve_fit(f, day, longitude, p0=initial_params)
    return initial_params, fitted_params

def plot_slopes(planet_name, day, longitude, initial_params, fitted_params):
    fig, axes = plt.subplots(len(initial_params), 1, figsize=(6.4, 12.8))

    N = 1000
    span = np.linspace(-1.0, 1.0, N)
    zero = span * 0.0
    one = span + 1.0
    print(span.shape, zero.shape, one.shape) # (1,100) all

    param_names = [
        'DT: deferent rotation period (days)',
        'D0: deferent angle at day=0.0',
        'xe: x coordinate of Earth',
        'ye: y coordinate of Earth',
        'ET: epicycle rotation period (days)',
        'E0: epicycle angle at day=0.0',
        'Er: epicycle radius (deferent radius=1)',
    ]
    scales = [10.0, 10.0, 0.25, 0.25, 10.0, 10.0, 0.3]
    assert len(scales) == len(fitted_params)

    def sum_of_squares(t, *params):
        D0 = params[1]
        y = to_longitude(equant_and_epicycle(t, *params), D0)
        delta = (longitude[:,None] - y)
        return (delta * delta).sum(axis=0)

    fitted_rss = sum_of_squares(day[:,None], *fitted_params)
    print('fitted_rss:', fitted_rss)

    for i, (param_name, scale) in enumerate(zip(param_names, scales)):
        param_arrays = initial_params[:,None] + zero  # (7,N)
        param_arrays[i] += span * scale
        this_param = param_arrays[i]

        x = this_param
        y = sum_of_squares(day[:,None], *param_arrays)
        axes[i].plot(x, y, ',')

        xi = initial_params[i]
        axes[i].plot(xi, np.interp(xi, x, y), 'o')

        xf = fitted_params[i]
        axes[i].plot(xf, fitted_rss, 'o')

        axes[i].set_xlabel(f'{param_name}')

    fig.tight_layout()
    fig.suptitle(planet_name + ': Residual sum-of-squares behavior of\n'
                 'each parameter around our initial guess\n'
                 '(the curve needs to be smooth!)\n'
                 'Orange: initial guess  Green: optimal')
    fig.subplots_adjust(top=0.90)  # Make room for suptitle
    fig.savefig(f'slopes_{planet_name}.png')

def plot_solution(planet_name, day, longitude, initial_params, fitted_params):
    fig, ax = plt.subplots(1,1)
    ax.plot(day, longitude,
            'g', label=f'Real-world {planet_name} longitude')

    D0 = initial_params[1]
    ax.plot(day, to_longitude(equant_and_epicycle(day, *initial_params), D0),
            'orange', label='Longitude produced by initial parameters')

    D0 = fitted_params[1]
    ax.plot(day, to_longitude(equant_and_epicycle(day, *fitted_params), D0),
            'b', label='Longitude produced by fitted parameters')

    ax.plot(day[::100], longitude[::100],
            '+g', label=f'Real-world {planet_name} longitude')

    ax.set(xlabel='Time (days)',
           ylabel='Geocentric apparent ecliptic longitude (°)')
    fig.legend()
    fig.tight_layout()
    fig.savefig(f'solution_{planet_name}.png')

def to_degrees(radians):
    return radians / tau * 360.0

def to_longitude(xy, D0):
    # Keep result’s first item to within 180° of D0.
    x, y = xy
    longitude = unwrap(arctan2(y, x), axis=0) / tau * 360.0
    offset = (D0 - longitude[0] + 180.0) // 360.0 * 360.0
    return offset + longitude

def to_radians(degrees):
    return degrees / 360.0 * tau

def equant_and_epicycle(t, DT, D0, xe, ye, ET, E0, Er):
    x1, y1 = equant_orbit(t, DT, D0, xe, ye)
    x2, y2 = epicycle(t, ET, E0, Er)
    return x1 + x2, y1 + y2

def equant_orbit(t, DT, D0, xe, ye):
    M = to_radians(D0) + t / DT * tau
    x, y = equant(M, xe, ye)
    return x + xe, y + ye

def equant(M, xe, ye):
    offset = arctan2(ye, xe)
    Mo = M - offset
    e = sqrt(xe*xe + ye*ye)
    a = Mo - arcsin(e * sin(Mo))
    a += offset
    return cos(a), sin(a)

def epicycle(t, ET, E0, Er):
    E = to_radians(E0) + t / ET * tau
    return Er * cos(E), Er * sin(E)

if __name__ == '__main__':
    main()
