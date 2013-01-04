"""Display an Earth globe.

Based on:

http://docs.enthought.com/mayavi/mayavi/auto/example_flight_graph.html

"""
import numpy as np
from mayavi import mlab

mlab.figure(1, bgcolor=(0.48, 0.48, 0.48), fgcolor=(0,0,0), size=(400, 400))
mlab.clf()

###############################################################################
from mayavi.sources.builtin_surface import BuiltinSurface
continents_src = BuiltinSurface(source='earth', name='Continents')

# on_ratio controls the level of detail of the continents
continents_src.data_source.on_ratio = 2
continents = mlab.pipeline.surface(continents_src, color=(0, 0, 0))

###############################################################################
# Display a semi-transparent sphere, for the surface of the Earth

# We use a sphere Glyph, throught the points3d mlab function, rather than
# building the mesh ourselves, because it gives a better transparent
# rendering.
sphere = mlab.points3d(0, 0, 0, scale_mode='none',
                                scale_factor=2,
                                color=(0.67, 0.77, 0.93),
                                resolution=50,
                                opacity=1.0,
                                name='Earth')

sphere.actor.property.specular = 0.20
sphere.actor.property.specular_power = 10

# Backface culling is necessary for more a beautiful transparent
# rendering.
sphere.actor.property.backface_culling = True

###############################################################################
# Plot the equator and the tropiques
theta = np.linspace(0, 2*np.pi, 100)
for angle in (-np.pi/6, 0, np.pi/6):
    x = np.cos(theta)*np.cos(angle)
    y = np.sin(theta)*np.cos(angle)
    z = np.ones_like(theta)*np.sin(angle)

    mlab.plot3d(x, y, z, color=(1, 1, 1),
                        opacity=0.2, tube_radius=None)

mlab.view(63.4, 73.8, 4, [-0.05, 0, 0])
mlab.show()
