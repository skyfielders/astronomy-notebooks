import numpy as np
from matplotlib import pyplot as plt

from skyfield.api import Star, load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection

# The comet is plotted on several dates `t_comet`.  But the stars only
# need to be drawn once, so we take the middle comet date as the single
# time `t` we use for everything else.

ts = load.timescale()
t = ts.utc(2020, 10, 26)

# The Hipparcos mission provides our star catalog.

with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)

# We will center the chart on the comet's middle position.

from skyfield.positionlib import ICRS, Barycentric, position_of_radec
barycenter = Barycentric([0,0,0], t=t)
#center = ICRS([1.0,1.0,1.0])
ra_hours = 6.0
dec_degrees = 45.0

def set_center(rot_a=0, rot_b=0):
    global center, projection, ra_hours, dec_degrees
    ra_hours += rot_a
    dec_degrees += rot_b
    center = position_of_radec(ra_hours, dec_degrees, center=0)
    #center.position.au[0] *= 1.01
    projection = build_stereographic_projection(center)

set_center()
field_of_view_degrees = 45.0
limiting_magnitude = 7.0

# Create a True/False mask marking the stars bright enough to be
# included in our plot.  And go ahead and compute how large their
# markers will be on the plot.

from time import time
print('Total stars:', stars.shape)
t0 = time()
#bright_stars = (stars.magnitude <= limiting_magnitude)
print(time() - t0, 's to filter all stars on 1 var')

#magnitude = stars['magnitude'] #[bright_stars]

# Now that we have constructed our projection, compute the x and y
# coordinates that each star and the comet will have on the plot.

star_positions = barycenter.observe(Star.from_dataframe(stars))

def set_positions():
    #t0 = time()
    stars['x'], stars['y'] = projection(star_positions)
    #print(time() - t0)

set_positions()

def run():
    # Time to build the figure!

    fig, ax = plt.subplots(figsize=[9, 9])

    # Draw the stars.

    def scatter_stars():
        marker_size = (0.5 + limiting_magnitude - stars['magnitude']) ** 2.0

        mask = (
            (marker_size > 0.25)
            & (stars['x'] > -0.3)
            & (stars['x'] < 0.3)
            & (stars['y'] > -0.3)
            & (stars['y'] < 0.3)
        )

        #print('Number of stars:', mask.sum())

        #scatter.set_data(stars['x'][mask], stars['y'][mask])
        xy = np.array([stars['x'][mask], stars['y'][mask]])
        scatter.set_offsets(xy.T)

        s = marker_size[mask] #[bright_stars]]
        scatter.set_sizes(s)

    scatter = ax.scatter([], [], color='k')
    scatter_stars()

    # Finally, title the plot and set some final parameters.

    angle = np.pi - field_of_view_degrees / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))
    #print(limit)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_aspect(1.0)
    ax.set_title('Stars')

    from ipywidgets import Label, HTML, HBox, Image, VBox, Box, HBox, interact
    from ipyevents import Event
    from IPython.display import display

    l = Label('Click or type on me!')
    l.layout.border = '2px solid red'

    h = HTML('Event info')
    d = Event(source=l, watched_events=['click', 'keydown', 'mouseenter'])

    def handle_event(event):
        lines = ['{}: {}'.format(k, v) for k, v in event.items()]
        content = '<br>'.join(lines)
        h.value = content

    d.on_dom_event(handle_event)

    #display(l, h)

    import ipywidgets as widgets

    def demo(i):
        field_of_view_degrees = 45.0 - i
        angle = np.pi - field_of_view_degrees / 360.0 * np.pi
        limit = np.sin(angle) / (1.0 - np.cos(angle))

        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        return fig

    #widgets.interact(demo, i = d)

    def callback(event):
        try:
            return callback2(event)
        except Exception as e:
            place.value = str(e)

    def callback2(event):
        nonlocal limit
        place.value = str(event['code'])
        code = event['code']
        if event['code'] == 'PageUp':
            limit /= 1.1
            ax.set_xlim(-limit, limit)
            ax.set_ylim(-limit, limit)
        elif event['code'] == 'PageDown':
            limit *= 1.1
            ax.set_xlim(-limit, limit)
            ax.set_ylim(-limit, limit)
        elif code.startswith('Arrow'):
            if code == 'ArrowUp':
                set_center(0, 0.5)
            elif code == 'ArrowDown':
                set_center(0, -0.5)
            elif code == 'ArrowLeft':
                set_center(0.1, 0)
            elif code == 'ArrowRight':
                set_center(-0.1, 0)
            set_positions()
            scatter_stars()
            place.value = 'Surv'

        #PageUp: bigger
        #    PageDown: smaller
        redraw()

    from io import BytesIO

    def redraw():
        io = BytesIO()
        plt.savefig(io, format="png")
        #plt.close()
        plt.ioff()
        image.value = io.getvalue()

    image = Image(format='png')
    redraw()

    # The layout bits below make sure the image display looks the same in lab and classic notebook 
    image.layout.max_width = '4in'
    image.layout.height = 'auto'

    im_events = Event()
    im_events.source = image
    im_events.watched_events = ['keydown']
    im_events.on_dom_event(callback)

    place = HTML('Test')
    return VBox([place, image])
