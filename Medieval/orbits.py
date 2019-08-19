import re
import numpy as np
import sympy as sy

tau = 2 * np.pi

CIRCULAR = '''
<svg version="1.1" width=220 height=220>
 <g transform="translate(110, 110)">
  <circle cx=0 cy=0 r=100 stroke=lightgray stroke-width=1 fill=none />
  <g class="%s">
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
 to {transform: rotate(360deg);}
}
</style>
'''

EQUANT = '''
<svg version="1.1" width=300 height=220>
 <g transform="translate(110, 110)">
  <circle cx=0 cy=0 r=2 fill=gray />
  <circle cx=0 cy=0 r=100 stroke=lightgray stroke-width=1 fill=none />
  <g class="planet">
   <circle cx=100 cy=0 r=5 fill=#bb0 />
  </g>
  <g transform="translate(%s, 0)">
   <circle cx=0 cy=0 r=2 fill=gray />
   <g class="uniform">
    <line x1=0 y1=0 x2=%s y2=0 stroke=lightgray />
   </g>
  </g>
 </g>
</svg>
<style>
.uniform, .planet {
  animation-duration: 10s;
  animation-iteration-count: infinite;
}
.uniform {
  animation-name: uniform;
  animation-timing-function: linear;
}
.planet {
  animation-name: planet;
}
@keyframes uniform {to {transform: rotate(360deg)}}
@keyframes planet {
%s
to { transform: rotate(360deg); }
}
</style>
'''

KEYFRAME = '''\
%.3f%% {
  transform: rotate(%.3frad);
  animation-timing-function: cubic-bezier(%.3f, %.3f, %.3f, %.3f);
}
'''

def bezier(t, x1, y1, x2, y2):
    m = 1 - t
    p = 3 * m * t
    b, c, d = p * m, p * t, t * t * t
    return (b * x1 + c * x2 + d,
            b * y1 + c * y2 + d)

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

def equant_svg(segments=4):
    e = 0.5
    M = linspace(0, tau, segments)
    keyframes = []
    for i, (M0, M1) in enumerate(zip(M[:-1], M[1:])):
        M = linspace(M0, M1)
        E = equant_E(M, e)
        E0, E1, params = equant_compute_approximate_segment(M0, M1, e)
        params = (100 * i/(segments - 1), E0) + tuple(params)
        keyframes.append(KEYFRAME % params)
    return EQUANT % (100 * e, 100 * (1 + e), ''.join(keyframes))

def compress_svg(svg):
    svg = re.sub(r'(\W)\s+(\W)', r'\1\2', svg)
    svg = re.sub(r'(\w)\s+(\W)', r'\1\2', svg)
    svg = re.sub(r'(\W)\s+(\w)', r'\1\2', svg)
    return svg

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
