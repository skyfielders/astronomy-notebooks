import numpy as np
import sympy as sy

tau = 2 * np.pi

CIRCULAR = '''
<svg version="1.1" width="220" height="220" xmlns="http://www.w3.org/2000/svg">
<g transform="translate(110, 110)">
<g class="rotating">
<line x1=0 y1=0 x2=100 y2=0 stroke=lightgray />
<circle cx=100 cy=0 r=5 fill=#bb0 />
</g>
<circle cx=0 cy=0 r=3 fill=#040 />
</g>
</svg>
<style>
.rotating {
animation-name: rotating;
animation-duration: 10s;
animation-timing-function: linear;
animation-iteration-count: infinite;
}
@keyframes rotating {
from { transform: rotate(0deg); }
to { transform: rotate(360deg); }
}
</style>
'''

EQUANT = '''
<svg version="1.1" width="300" height="220" xmlns="http://www.w3.org/2000/svg">
<g transform="translate(110, 110)">
<g class="equant">
<circle cx=100 cy=0 r=5 fill=#bb0 />
</g>
<g transform="translate(%s, 0)">
<g class="uniform">
<line x1=0 y1=0 x2=200 y2=0 stroke=lightgray />
</g>
</g>
<circle cx=0 cy=0 r=3 fill=#040 />
</g>
</svg>
<style>
.uniform, .equant {
  animation-duration: 10s;
  animation-iteration-count: infinite;
}
.uniform {
  animation-name: uniform;
  animation-timing-function: linear;
}
.equant {
  animation-name: equant;
}
@keyframes uniform {
from { transform: rotate(0deg); }
to { transform: rotate(360deg); }
}
@keyframes equant {
0%% {
  transform: rotate(%srad);
  animation-timing-function: cubic-bezier(%s);
}
33.33%% {
  transform: rotate(%srad);
  animation-timing-function: cubic-bezier(%s);
}
66.66%% {
  transform: rotate(%srad);
  animation-timing-function: cubic-bezier(%s);
}
to { transform: rotate(360deg); }
}
</style>
'''

def bezier(t, x1, y1, x2, y2):
    mt = 1 - t
    c = 3 * mt * t
    c1, c2, c3 = c * mt, c * t, t * t * t
    return (c1 * x1 + c2 * x2 + c3,
            c1 * y1 + c2 * y2 + c3)

def bezier_interpolated(x, x1, y1, x2, y2):
    t = linspace(0, 1)
    xb, yb = bezier(t, x1, y1, x2, y2)
    y = np.interp(x, xb, yb)
    return y

def equant_E(M, e):
    return M - arcsin(e * np.sin(M))

from numpy import abs, arcsin, linspace, max, sin
from scipy.optimize import curve_fit

def equant_compute_approximate_segment(M0, M1, e):
    M = linspace(M0, M1)
    E = equant_E(M, e)
    E0 = E[0]
    E1 = E[-1]
    x = linspace(0, 1)
    y = (E - E0) / (E1 - E0)
    args, variance = curve_fit(
        bezier_interpolated, x, y,
        [0.5, 0.0, 0.5, 1.0],
        bounds=[0, 1],
    )
    return E0, E1, args

def equant_approximate_segment(M0, M1, E0, E1, args):
    x = linspace(0, 1)
    M = linspace(M0, M1)
    return E0 + (E1 - E0) * bezier_interpolated(x, *args)

def max_errors(M, e):
    errors = []
    for M0, M1 in zip(M[:-1], M[1:]):
        M = linspace(M0, M1)
        E = equant_E(M, e)
        E0, E1, args = equant_compute_approximate_segment(M0, M1, e)
        error = E - equant_approximate_segment(M0, M1, E0, E1, args)
        errors.append(abs(error).max())
    return np.array(errors)

def equant_svg():
    params = [5.45569942e-01, 6.77191311e-19, 4.54430058e-01, 1.00000000e+00]
    paramstr = ','.join(repr(n) for n in params)
    return EQUANT % paramstr

def equant_svg2():
    e = 0.5
    paramstrs = [100 * e]
    M = linspace(0, tau, 4)
    for M0, M1 in zip(M[:-1], M[1:]):
        M = linspace(M0, M1)
        E = equant_E(M, e)
        E0, E1, params = equant_compute_approximate_segment(M0, M1, e)
        paramstrs.append(E0)
        paramstrs.append(','.join(repr(n) for n in params))
    return EQUANT % tuple(paramstrs)

def circular(t):
    return CIRCULAR

def equant_general(t, M0, n, xE, yE, xQ, yQ, R):
    pass

def solve_equant():
    a, b = sy.symbols('a b')
    x = sy.solve([
        a - b - 3,
        a + b,
    ], (a,b))
    print(x)

    equant_x = 1
    equant_y = 3

    #t, x, y, xE, yE, M = sy.symbols('t x y xE yE M')
    x, y, xE, yE, M = sy.symbols('x y xE yE M')
    soln = sy.solve([
        M * tau - sy.atan2(y - yE, x - xE),
        x * x + y * y - 1,
    ], (x, y))
    return soln

def solve_equant2():
    x_Q, y_Q, M, C = sy.symbols('x_Q y_Q M C')
    x = sy.cos(C)
    y = sy.sin(C)
    return sy.solve([
        M - sy.atan2(y - y_Q, x - x_Q),
        ], C)

from sympy import sin, cos, tan, atan2

def solve_equant3():
    # E: eccentric anomaly = angle viewed from center
    # M: mean anomaly = angle from equant
    # e: eccentricity = distance from center to equant
    e, M, E = sy.symbols('e M E')
    return sy.solve([
        #tan(M) - sin(E) / (cos(E) - e)
        M - atan2(sin(E), cos(E) - e)
    ], E)

from sympy import sqrt, tan, pi, cos

def solns():
    t, x, y, xE, yE, M = sy.symbols('t x y xE yE M')
    return [(-sqrt((-2*xE*tan(pi*M)**3 + 2*xE*tan(pi*M) - yE*tan(pi*M)**4 + 2*yE*tan(pi*M)**2 - yE - 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*(2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE + 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*cos(pi*M)**8),
  (2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE + 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M))*cos(pi*M)**4),
 (sqrt((-2*xE*tan(pi*M)**3 + 2*xE*tan(pi*M) - yE*tan(pi*M)**4 + 2*yE*tan(pi*M)**2 - yE - 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*(2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE + 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*cos(pi*M)**8),
  (2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE + 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M))*cos(pi*M)**4),
 (-sqrt((-2*xE*tan(pi*M)**3 + 2*xE*tan(pi*M) - yE*tan(pi*M)**4 + 2*yE*tan(pi*M)**2 - yE + 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*(2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE - 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*cos(pi*M)**8),
  (2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE - 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M))*cos(pi*M)**4),
 (sqrt((-2*xE*tan(pi*M)**3 + 2*xE*tan(pi*M) - yE*tan(pi*M)**4 + 2*yE*tan(pi*M)**2 - yE + 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*(2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE - 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M) + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*cos(pi*M)**8),
  (2*xE*tan(pi*M)**3 - 2*xE*tan(pi*M) + yE*tan(pi*M)**4 - 2*yE*tan(pi*M)**2 + yE - 2*sqrt(-4*xE**2*tan(pi*M)**2 - 4*xE*yE*tan(pi*M)**3 + 4*xE*yE*tan(pi*M) - yE**2*tan(pi*M)**4 + 2*yE**2*tan(pi*M)**2 - yE**2 + tan(pi*M)**4 + 2*tan(pi*M)**2 + 1)*tan(pi*M))*cos(pi*M)**4),
 (-sqrt(1 - yE**2), yE),
 (sqrt(1 - yE**2), yE)]

def equant_general(t, M0, n, equant_x, equant_y):
    pass
