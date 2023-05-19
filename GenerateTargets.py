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
# base_origin = np.array([-325 - 35.8, -665 - 1641.2])  # 2023-05-16
base_origin = np.array([-325.6 - 35.8, -665 - 1641.2])  # 2023-05-17

# Define the used utility classes
coord = TileBoardCoordinates(base_origin=base_origin, base_rotation=90)
board = TileBoard(coord)

# Generate reasonable hit positions in the polar coordinate system
# angles = board.SiPM_angles + 0.25
# radii = board.SiPM_radii + 7
#
# all_angles = np.tile(angles, 8)
# all_radii = np.repeat(radii, 8)

# Generate positions for shower measurements
all_angles = np.array([-1.25, 1.25])
all_radii = np.array([
    (board.SiPM_radii[2] + board.SiPM_radii[1]) / 2,
    (board.SiPM_radii[4] + board.SiPM_radii[3]) / 2,
])

# Convert the positions to the cartesian system
x_hits, y_hits = coord.PolarToCartesian(all_radii, all_angles)
x_hits = -x_hits  # Coordinate system at the test beam is opposite

# New order for channels for the scanner
base_row = np.arange(0, 8, 1, dtype=int)
new_index = base_row
for i in range(1, 8):
    new_index = np.concatenate([new_index, (np.flip(base_row) if i % 2 == 1 else base_row) + i * 8])

# Write the hit positions to a CSV file
# df = pd.DataFrame(data={"ch": board.SiPM_channels, "x": x_hits, "y": y_hits})
df = pd.DataFrame(data={"ch": ["pos1", "pos2"], "x": x_hits, "y": y_hits})
# df = df.loc[new_index]
df = df[~df["ch"].isin(board.SiPM_empty_channels)]
df.to_csv("hit_positions.csv")

# Draw the positions for debugging
ax = plt.gca()
ax.set_aspect("equal")

board.DrawOutline(ax)
board.DrawSiPMs(ax, label_pos=False)
board.DrawTiles(ax)

# board.DrawSiPMs(ax, radii=radii, angles=angles, format_str="rx")
ax.step(-df.x, df.y, "rx:")

plt.show()
