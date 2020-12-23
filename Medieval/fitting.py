#!/usr/bin/env python3
"""

http://farside.ph.utexas.edu/Books/Syntaxis/Almagest.pdf
https://people.sc.fsu.edu/~dduke/inner.pdf

"""
import matplotlib.pyplot as plt
import numpy as np
import sys
from collections import defaultdict
from numpy import arcsin, arctan2, cos, sin, unwrap, sqrt
from scipy.optimize import curve_fit
from skyfield.api import load, tau

# Several potentially independent parameters in Ptolemy’s model are
# required to have the same value, and should be given to the solver as
# a single value.  Our “SCHEME” assigns a unique name to each parameter,
# that we use to remove duplicates when submitting them to the solver.

SCHEME = """\
Moon    lun.DT lun.D0 lun.xe lun.ye
Mercury sun.DT sun.D0 mer.xe mer.ye mer.ET mer.E0 mer.Er
Venus   sun.DT sun.D0 ven.xe ven.ye ven.ET ven.E0 ven.Er
Sun     sun.DT sun.D0 sun.xe sun.ye
Mars    mar.DT mar.D0 mar.xe mar.ye sun.DT sun.D0 mar.Er
Jupiter jup.DT jup.D0 jup.xe jup.ye sun.DT sun.D0 jup.Er
Saturn  sat.DT sat.D0 sat.xe sat.ye sun.DT sun.D0 sat.Er
"""
SCHEME = [line.split() for line in SCHEME.splitlines()]

YEARS = 10
planet_names = 'Moon Mercury Venus Sun Mars Jupiter Saturn'.split()

def main():
    ts = load.timescale()
    t = ts.tt(2010, 1, range(366 * YEARS))
    day = t.tt - t.tt[0]  # timescale: TT days from start of time range

    ephemeris = load('de421.bsp')
    earth = ephemeris['Earth']
    longitudes = []

    for planet_name in planet_names:
        print(f'Asking ephemeris for {planet_name} positions')
        try:
            planet = ephemeris[planet_name]
        except KeyError:
            planet = ephemeris[planet_name + ' barycenter']
        lat, lon, distance = earth.at(t).observe(planet).ecliptic_latlon()
        longitude = to_degrees(unwrap(lon.radians))
        longitudes.append(longitude)

    announce('Generating initial parameter guesses')
    parameter_lists = [generate_initial_params(day, longitude)
                       for longitude in longitudes]

    announce('Optimizing parameters')
    parameter_dict = average_parameters(parameter_lists)
    print(parameter_dict)
    parameter_dict = fit_parameters(day, longitudes, parameter_dict)
    print(parameter_dict)

    announce('Saving results')
    for planet_name, *names in SCHEME:
        fitted_params = [parameter_dict[name] for name in names]
        with open(f'parameters_{planet_name}.txt', 'w') as f:
            print(list(fitted_params), file=f)

    if len(sys.argv) < 2:
        return

    z = zip(SCHEME, longitudes, parameter_lists)
    for (planet_name, *names), longitude, initial_params in z:
        fitted_params = [parameter_dict[name] for name in names]
        announce(f'Plotting {planet_name}')
        plot_slopes(planet_name, day, longitude, initial_params, fitted_params)
        plot_solution(planet_name, day, longitude, initial_params,
                      fitted_params)

def announce(text):
    print(f' {text} '.center(78, '='))

def generate_initial_params(day, longitude):
    derivative_sign_diff = np.diff(np.sign(np.diff(longitude)))
    retrograde_starts, = np.nonzero(derivative_sign_diff < 0)

    if not len(retrograde_starts):
        # No retrograde motion: use only a deferent.

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

        E0 = longitude[m[0]] + 180.0 - 360.0 * (day[m[0]] / ET)
        E0 %= 360.0

        initial_params = np.array([DT, D0, 0, 0, ET, E0, 0.5])

    return initial_params

def average_parameters(parameter_lists):
    """Return a dict with each parameter's average value."""
    value_lists = defaultdict(list)
    for (planet_name, *names), parameters in zip(SCHEME, parameter_lists):
        for name, parameter in zip(names, parameters):
            value_lists[name].append(parameter)
    return {name: sum(values) / len(values)
            for name, values in sorted(value_lists.items())}

def fit_parameters(day, longitudes, parameter_dict):
    # SciPy’s curve_fit() only supports positional arguments, so let’s
    # use alphabetical order for the parameters.
    parameter_names = sorted(parameter_dict.keys())

    # Make curve_fit()’s job easier by pretending all 7 longitude traces
    # are a single long curve.
    longitude = np.concatenate(longitudes)

    def f(day, *parameter_list):
        parameter_dict = dict(zip(parameter_names, parameter_list))
        longitudes = []
        for planet, *names in SCHEME:
            values = [parameter_dict[name] for name in names]
            if len(values) == 4:
                xy = equant_orbit(day, *values)
            else:
                xy = equant_and_epicycle(day, *values)
            D0 = values[1]
            longitudes.append(to_longitude(xy, D0))
        return np.concatenate(longitudes)

    p0 = [parameter_dict[name] for name in parameter_names]
    fitted_params, etc = curve_fit(f, day, longitude, p0=p0)
    parameter_dict = dict(zip(parameter_names, fitted_params))
    return parameter_dict

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
    scales = [10.0, 10.0, 0.25, 0.25, 10.0, 10.0, 0.3][:len(initial_params)]

    def sum_of_squares(t, *params):
        D0 = params[1]
        if len(params) == 4:
            y = to_longitude(equant_orbit(t, *params), D0)
        else:
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

    # The crosses help me see where the real longitude curve is, even
    # when hidden by a very good fit of the Ptolemy curve.
    ax.plot(day[::100], longitude[::100],
            '+g', label=f'Real-world {planet_name} longitude')

    D0 = initial_params[1]
    ax.plot(day, to_longitude(equant_and_epicycle(day, *initial_params), D0),
            'orange', label='Longitude produced by initial parameters')

    D0 = fitted_params[1]
    ax.plot(day, to_longitude(equant_and_epicycle(day, *fitted_params), D0),
            'b', label='Longitude produced by fitted parameters')

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

def equant_and_epicycle(t, DT, D0, xe, ye, ET=1, E0=0, Er=0):
    x1, y1 = equant_orbit(t, DT, D0, xe, ye)
    x2, y2 = epicycle(t, ET, E0, Er)
    return x1 + x2, y1 + y2

def equant_orbit(t, DT, D0, xe, ye):
    M = to_radians(D0) + t / DT * tau
    x, y = equant(M, xe, ye)
    return x + xe, y + ye

def equant(M, xe, ye):
    "M: mean anomaly in radians; xe, ye: location of equant."
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
