from numpy import arcsin, arctan2, cos, pi, sin, unwrap, sqrt

tau = 2 * pi

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

