import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from TileBoardCoordinates import *

base_origin = np.array([-325 - 35.8, -665 - 1641.2])

coord = TileBoardCoordinates(base_origin=base_origin, base_rotation=90)
board = TileBoard(coord)


# Generate reasonable hit positions
angles = board.SiPM_angles + 0.25
radii = board.SiPM_radii + 7

all_angles = np.tile(angles, 8)
all_radii = np.repeat(radii, 8)

print(all_angles)
print(all_radii)

x_hits, y_hits = coord.PolarToCartesian(all_radii, all_angles)
x_hits = -x_hits

df = pd.DataFrame(data={"ch": board.SiPM_channels, "x": x_hits, "y": y_hits})
df.to_csv("hit_positions.csv")


# Get drawing axes
ax = plt.gca()
ax.set_aspect("equal")

board.DrawOutline(ax)
board.DrawSiPMs(ax, label_pos=False)
board.DrawTiles(ax)

board.DrawSiPMs(ax, radii=radii, angles=angles, format_str="rx")


plt.show()