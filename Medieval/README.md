
# Welcome to an animated Ptolemy cosmos!

When writing the title of this README,
I almost typed “animated Ptolemy solar system”,
but of course it’s not a “solar system”
because it doesn’t revolved around the Sun
but around the Earth.

This directory holds the code
for generating my web site’s animation
of the medieval model of the universe
which it inherited from the ancient scientist Ptolemy:

https://rhodesmill.org/ptolemy/

It works like this:

    fitting.py - Uses the Skyfield library + a JPL
      ephemeris file to generate planet positions,
      then uses a SciPy optimize routine to figure
      out what sized equants and epicycles will
      best model the planets’ motions.

    ↓

    parameters_*.txt - Equant and epicycle parameters
    slopes_*.png - Displays whether the initial guess
      that’s given to the SciPy optimizer for each
      parameter is surrounded by a smooth slope
      towards a better solution, or not.
    solution_*.png - Plots of real planet motions vs
      how the computed equants and epicycles would
      move the planet.

    ↓      ⬐ texts.html

    build_animation.py - Reads in the parameters files
      and builds HTML pages that embed SVG animations
      focused on the outer planets and inner planets.

    ↓

    out/*.html


There’s also an `orbit_math.py` module of several
routines shared between the other Python files,
and a little `report.py` script that displays a quick
table showing how big each planet’s orbit is
in Earth radii.
