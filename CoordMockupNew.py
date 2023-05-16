import numpy as np
import matplotlib.pyplot as plt

from TileBoardCoordinates import *


coord = TileBoardCoordinates(base_origin=np.array([0, -1791.1]), base_rotation=90)
board = TileBoard(coord)

# Track mouse position
def mouse_move(event):
    x, y = event.xdata, event.ydata
    if x is not None and y is not None:
        r, phi = coord.CartesianToPolar(x, y)
        plt.title("r, phi = {:.2f}, {:.2f}\n Channel {}".format(r, phi, board.GetChannelByPosition(x, y)))
        plt.draw()

plt.connect('motion_notify_event', mouse_move)


# Get drawing axes
ax = plt.gca()
ax.set_aspect("equal")

board.DrawOutline(ax)
board.DrawSiPMs(ax, label_pos=False)
board.DrawTiles(ax)


plt.show()