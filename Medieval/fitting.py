#!/usr/bin/env python3

import sympy as sy
from numpy import arcsin, cos, sin, unwrap, arctan
from scipy.optimize import curve_fit
from skyfield.api import load, tau

def main():
    solve_equant()
    return
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

    print(T, M0, e, ω)

    T, M0, e, ω, Tₑ, E0, r = fit_equant_and_epicycle(
        days, longitude, T, M0, e, ω,
    )

    print(T, M0, e, ω, Tₑ, E0, r)

    # Normalize negative e by rotating the orbit 180°.
    # if e < 0:
    #     e = -e
    #     ω += tau/2
    #     M0 -= tau/2

    # # Normalize ω.
    # offset, ω = divmod(ω, tau)
    # M0 += offset * tau

    residual = equant(day, T, M0, e, ω) - longitude

    ax.plot(day, degrees(residual))
    ax.plot(day, degrees(equant(day, T, M0, e, ω) + epicycle(day, Tₑ, E0, r)
                         - longitude))
    #ax.plot(day, degrees(equant(day, T, ω, -e)) - degrees(lon))
    #ax.plot(day, degrees(equant(day, T, ω-tau/2, -e)+tau/2) - degrees(lon))

    # ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='Title')
    # ax.set_aspect(aspect=1.0)
    # ax.grid()
    # plt.legend()
    fig.savefig('tmp.png')

from scipy.optimize import fsolve

# [{x: -sqrt(1 - y**2), M: 2*atan((-ey + y + sqrt(ex**2 + 2*ex*sqrt(1 - y**2) + ey**2 - 2*ey*y + 1))/(ex + sqrt(1 - y**2)))}, {x: -sqrt(1 - y**2), M: -2*atan((ey - y + sqrt(ex**2 + 2*ex*sqrt(1 - y**2) + ey**2 - 2*ey*y + 1))/(ex + sqrt(1 - y**2)))}]

# [(ex - ey*tan(M) - (ex*sin(2*M) + ey*cos(2*M) - ey - sqrt(2)*sqrt(-ex**2*cos(2*M) - ex**2 + 2*ex*ey*sin(2*M) + ey**2*cos(2*M) - ey**2 + 2)*cos(M))*tan(M)/2, -ex*sin(2*M)/2 - ey*cos(2*M)/2 + ey/2 + sqrt(2)*sqrt(-ex**2*cos(2*M) - ex**2 + 2*ex*ey*sin(2*M) + ey**2*cos(2*M) - ey**2 + 2)*cos(M)/2), (ex - ey*tan(M) - (ex*sin(2*M) + ey*cos(2*M) - ey + sqrt(2)*sqrt(-ex**2*cos(2*M) - ex**2 + 2*ex*ey*sin(2*M) + ey**2*cos(2*M) - ey**2 + 2)*cos(M))*tan(M)/2, -ex*sin(2*M)/2 - ey*cos(2*M)/2 + ey/2 - sqrt(2)*sqrt(-ex**2*cos(2*M) - ex**2 + 2*ex*ey*sin(2*M) + ey**2*cos(2*M) - ey**2 + 2)*cos(M)/2)]

from numpy import tan, sqrt

def equant(ex, ey, M):
    x = ex - ey*tan(M) - (ex*sin(2*M) + ey*cos(2*M) - ey - sqrt(2)*sqrt(-ex**2*cos(2*M) - ex**2 + 2*ex*ey*sin(2*M) + ey**2*cos(2*M) - ey**2 + 2)*cos(M))*tan(M)/2
    y = -ex*sin(2*M)/2 - ey*cos(2*M)/2 + ey/2 + sqrt(2)*sqrt(-ex**2*cos(2*M) - ex**2 + 2*ex*ey*sin(2*M) + ey**2*cos(2*M) - ey**2 + 2)*cos(M)/2
    return x, y

def solve_equant():
    # print(equant(-0.99, 0, 0.1))
    # print(equant(-0.99, 0, 0.2))
    # print(equant(-0.99, 0, 0.3))
    # from time import time
    # t0 = time()
    # #soln = fsolve(eqeqeq, 1.0, (0.5, 1.0, tau/8.0))
    # soln = fsolve(eqeqeq, 1.0, (0.9, 0.0, tau/12.0)) #, full_output=True)
    # print(time() - t0)
    # print(soln)
    return

    # a, b = sy.symbols('a b')
    # x = sy.solve([
    #     a - b - 3,
    #     a + b,
    # ], (a,b))
    # print(x)

    # x = sin(M)
    # y = cos(M)

    x, y, xe, ye, M = sy.symbols('x y ex ey M')
    # x = xe + r * sin(M)
    # y = ye + r * cos(M)
    
    # x = xe + r * sin(M)
    # y = ye + r * cos(M)

    # (x - xe) / sin(M) = r
    # (y - ye) / cos(M) = r

    # (x - xe) / sin(M) = (y - ye) / cos(M)

    #return x*x + y*y - 1
    o = sy.solve([
        1 - x*x - y*y,
        (x - xe) / sy.sin(M) - (y - ye) / sy.cos(M),
        #M - sy.atan2(y - ey, x - ex),
    ], [x, y])
    print(o)

    # ex, ey, M, x, y = sy.symbols('ex ey M x y')
    # o = sy.solve([
    #     1 - x*x - y*y,
    #     M - sy.atan2(y - ey, x - ex),
    # ])
    # print(o)

def eqeqeq(r, xe, ye, M):
    x = xe + r * sin(M)
    y = ye + r * cos(M)
    return x*x + y*y - 1

    # x, y = xy
    # ex, ey = 0.5, 0.0
    # M = tau / 8.0
    # return x*x + y*y - 1, M - arctan(

def foo():
    pass

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

def fit_equant_and_epicycle(day, longitude, T, M0, e, ω):
    Tₑ = 300
    E0 = 0
    r = 0.5

    def f(t, Tₑ, E0, r):
        return equant(t, T, M0, e, ω) + epicycle(t, Tₑ, E0, r)

    (Tₑ, E0, r), covariance = curve_fit(f, day, longitude, (Tₑ, E0, r))

    # def f(t, T, M0, e, ω, Tₑ, E0, r):
    #     return equant(t, T, M0, e, ω) + epicycle(t, Tₑ, E0, r)

    # Normalize negative e by rotating the orbit 180°.
    if e < 0:
        e = -e
        ω += tau/2
        M0 -= tau/2

    # Normalize ω.
    offset, ω = divmod(ω, tau)
    M0 += offset * tau

    return T, M0, e, ω, Tₑ, E0, r

def degrees(radians):
    return radians / tau * 360.0

def equant2(t, T, ex, ey):
    M = t / T * tau
    x = 2 * e
    #y =
    # x =
    # y =
    angle = ω + M - arcsin(e * sin(M))

def epicycle(t, Tₑ, E0, r):
    E = E0 + t / Tₑ * tau
    return r * sin(E)

if __name__ == '__main__':
    main()
