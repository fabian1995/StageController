import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math


class TileBoardCoordinates:
    def __init__(self, base_origin=np.array([0, 0]), base_rotation=90):
        self.base_origin = base_origin
        self.base_rotation = base_rotation

    def PolarToCartesian(self, r, phi):
        x = r * np.cos((phi + self.base_rotation) * np.pi/180) + self.base_origin[0]
        y = r * np.sin((phi + self.base_rotation) * np.pi/180) + self.base_origin[1]
        return x, y

    def CartesianToPolar(self, x, y):
        x = x - self.base_origin[0]
        y = y - self.base_origin[1]
        r = np.sqrt(x**2 + y**2)
        phi = np.arctan(y / x) * 180 / np.pi + self.base_rotation
        if phi >= 90:
            phi = -180 + phi
        return r, phi

    def Transform(self, x, y, r, phi):
        x = x + self.PolarToCartesian(r, phi)[0]
        y = y + self.PolarToCartesian(r, phi)[1]
        return x, y

    def Rotate(self, x, y, phi):
        # phi += self.base_rotation
        x1 = x * np.cos(math.radians(phi)) - y * np.sin(math.radians(phi))
        y1 = x * np.sin(math.radians(phi)) + y * np.cos(math.radians(phi))
        return x1, y1


class TileBoard:
    def __init__(self, coordinates):
        self.coordinates = coordinates

        self.SiPM_angles = np.array([-4.375, -3.125, -1.875, -0.625, 0.625, 1.875, 3.125, 4.375])
        self.SiPM_radii = np.array([1554.19, 1588.47, 1623.515, 1659.325, 1695.93, 1733.33, 1771.56, 1810.635])
        self.SiPM_channels = [69, 71, 65, 67, 60, 62, 56, 58, 68, 70, 64, 66, 59, 61, 55, 57, 41, 43, 37, 39, 50, 52,
                            46, 48, 40, 42, 36, 38, 49, 51, 45, 47, 20, 22, 33, 35, 29, 31, 24, 26, 19, 21, 32, 34,
                            28, 30, 23, 25, 14, 16, 10, 12, 1, 3, 5, 7, 13, 15, 9, 11, 0, 2, 4, 6]

        self.Tile_h = np.array([34.28, 34.28, 35.18, 35.18, 37.40, 37.40, 39.07, 39.07]) * 0.9
        self.Tile_a = np.array([33.53, 33.53, 35.03, 35.03, 36.59, 36.59, 37.41, 37.41]) / 2
        self.Tile_b = np.array([34.28, 34.28, 35.81, 35.81, 36.80, 36.80, 38.47, 38.47]) * 0.95

        self.Board_angles = np.array([-5, 5])
        self.Board_radii = np.array([1537.05, 1537.05 + 292.5])


    def GetChannelByPosition(self, x, y):
        r, phi = self.coordinates.CartesianToPolar(x, y)
        if phi < self.Board_angles[0] or phi > self.Board_angles[1] or r < self.Board_radii[0] or r > self.Board_radii[1]:
            return -2

        slice_fraction = 5 / 4.
        slice_index = int((phi + 5) / slice_fraction)
        phi_rest = phi - slice_fraction/2 - (slice_index - 4) * slice_fraction

        # Use the symmetry
        phi_rest = np.abs(phi_rest)
        c1 = TileBoardCoordinates(base_rotation=90)
        x1, y1 = c1.PolarToCartesian(r, phi_rest)
        tile_h1 = self.SiPM_radii - self.Tile_h / 2
        tile_h2 = self.SiPM_radii + self.Tile_h / 2

        for h_index in range(self.SiPM_radii.size):
            if y1 >= tile_h1[h_index] and y1 <= tile_h2[h_index]:
                break
        else:
            return -1

        a = self.Tile_a[h_index]
        b = self.Tile_b[h_index]
        h = self.Tile_h[h_index]
        k = 2 * h / (b - a)
        d = self.SiPM_radii[h_index] - h/2 - k * a/2

        if y1 > k * x1 + d:
            return self.SiPM_channels[h_index * self.SiPM_radii.size + slice_index]

        return "{}, {}".format(x1, y1)


    def DrawOutline(self, ax, detail=30):
        r1 = self.Board_radii[0]
        r2 = self.Board_radii[1]
        theta1 = self.Board_angles[0]
        theta2 = self.Board_angles[1]

        ax.plot(*self.coordinates.PolarToCartesian(self.Board_radii, np.full(2, self.Board_angles[0])), color="k")
        ax.plot(*self.coordinates.PolarToCartesian(self.Board_radii, np.full(2, self.Board_angles[1])), color="k")
        ax.plot(*self.coordinates.PolarToCartesian(np.full(detail, r1), np.linspace(*self.Board_angles, detail)), color="k")
        ax.plot(*self.coordinates.PolarToCartesian(np.full(detail, r2), np.linspace(*self.Board_angles, detail)), color="k")

    def DrawSiPMs(self, ax, label_pos=False):
        x = []
        y = []
        i = 0
        for r in self.SiPM_radii:
            for phi in self.SiPM_angles:
                xi, yi = self.coordinates.PolarToCartesian(r, phi)
                x.append(xi)
                y.append(yi)
                label = "{}".format(self.SiPM_channels[i])
                if label_pos:
                    label += "\n({:.2f}, {:.2f})".format(xi, yi)
                ax.text(xi, yi, label)
                i += 1

        ax.scatter(x, y)

    def DrawTiles(self, ax):
        for r, h, a, b in zip(self.SiPM_radii, self.Tile_h, self.Tile_a, self.Tile_b):
            x = np.array([-a/2, a/2, b/2, -b/2])
            y = np.array([-h/2, -h/2, h/2, h/2])
            for phi in self.SiPM_angles:
                x1, y1 = self.coordinates.Rotate(x, y, phi - 90 + self.coordinates.base_rotation)
                x1, y1 = self.coordinates.Transform(x1, y1, r, phi)
                ax.add_patch(patches.Polygon(xy=list(zip(x1, y1)), facecolor="c", alpha=0.3, edgecolor="b"))



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