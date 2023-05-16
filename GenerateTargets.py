""" GenerateTargets.py

A script used during the tileboard test beam at DESY on 2023-05-16.
This script generates a CSV file with beam positions that can be used for the
automatic stage to scan every tile on the tileboard.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from TileBoardCoordinates import *

# This origin we determined by finding where the beam hits the board.
# It should be different every time you move the setup.
base_origin = np.array([-325 - 35.8, -665 - 1641.2])

# Define the used utility classes
coord = TileBoardCoordinates(base_origin=base_origin, base_rotation=90)
board = TileBoard(coord)

# Generate reasonable hit positions in the polar coordinate system
angles = board.SiPM_angles + 0.25
radii = board.SiPM_radii + 7

all_angles = np.tile(angles, 8)
all_radii = np.repeat(radii, 8)

# Convert the positions to the cartesian system
x_hits, y_hits = coord.PolarToCartesian(all_radii, all_angles)
x_hits = -x_hits

# Write the hit positions to a CSV file
df = pd.DataFrame(data={"ch": board.SiPM_channels, "x": x_hits, "y": y_hits})
df.to_csv("hit_positions.csv")

# Draw the positions for debugging
ax = plt.gca()
ax.set_aspect("equal")

board.DrawOutline(ax)
board.DrawSiPMs(ax, label_pos=False)
board.DrawTiles(ax)

board.DrawSiPMs(ax, radii=radii, angles=angles, format_str="rx")

plt.show()
