""" TileBoardCoordinates.py

Contains two classes:
 * TileBoardCoordinates, a utility class to define a coordinate system and
   convert between cartesian and polar coordinates.
 * TileBoard, a class that contains the geometry definition of a tileboard,
   utility functions and drawing.
"""

import numpy as np
import math
import matplotlib.patches as patches

class TileBoardCoordinates:
    """
    Utility class to define a coordinate system for the tileboard. Contains
    functions to convert between polar and cartesian coordinates, as well
    as rotations and transformations.

    Args:
        base_origin (np.array): x and y offset of the origin
        base_rotation (float): Initial rotation of the coordinate system in
            degrees (between 0 and 360).
    """
    def __init__(self, base_origin=np.array([0, 0]), base_rotation=90):
        self.base_origin = base_origin
        self.base_rotation = base_rotation

    def PolarToCartesian(self, r, phi):
        """
        Transforms a set of polar coordinates to cartesian coordinates.
        Takes initial rotation and coordinate offset into account.

        Args:
            r (float or np.array): Radius or list of radii
            phi (floar or np.array): Angle or list of angles

        Returns:
            x, y: List of cartesian coordinates
        """
        x = r * np.cos((phi + self.base_rotation) * np.pi/180) + self.base_origin[0]
        y = r * np.sin((phi + self.base_rotation) * np.pi/180) + self.base_origin[1]
        return x, y

    def CartesianToPolar(self, x, y):
        """
        Transforms a set of cartesian coordinates to polar coordinates.
        Takes initial rotation and coordinate offset into account.

        Args:
            x, y (float or np.array): Lists of coordinates.

        Returns:
            r, phi: Lists of polar coordinates
        """
        x = x - self.base_origin[0]
        y = y - self.base_origin[1]
        r = np.sqrt(x**2 + y**2)
        phi = np.arctan(y / x) * 180 / np.pi - self.base_rotation
        if phi <= -270:
            phi = 360 + phi
        elif phi <= -90:
            phi = 180 + phi
        elif phi >= 90:
            phi = -180 + phi
        return r, phi

    def Transform(self, x, y, r, phi):
        """
        Shifts a set of points by a distance r in direction phi.
        Takes initial rotation and coordinate offset into account.

        Args:
            x, y (float or np.array): Cartesian coordinates of the points to
                be moved.
            r (float): Distance that each point will move.
            phi (float): Angle for the move operation.

        Returns:
            x, y (float or np.array): New cartesian positions of the points.
        """
        x = x + self.PolarToCartesian(r, phi)[0]
        y = y + self.PolarToCartesian(r, phi)[1]
        return x, y

    def Rotate(self, x, y, phi):
        """
        Rotates a set of points around (0, 0) by an angle phi.

        Args:
            x, y (float or np.array): Cartesian coordinates of the points to
                be rotated around (0, 0).
            phi (float): Angle for the rotation.

        Returns:
            x, y (float or np.array): New cartesian positions of the points.
        """
        x1 = x * np.cos(math.radians(phi)) - y * np.sin(math.radians(phi))
        y1 = x * np.sin(math.radians(phi)) + y * np.cos(math.radians(phi))
        return x1, y1


class TileBoard:
    """
    This class specifies the geometry of a tileboard and contains some utility
    functions for drawing and geometric calculations.
    Currently, the D8 geometry is hard-coded in the constructor.

    Args:
        coordinates: The coordinate system, an instance of TileBoardCoordinates.
    """
    def __init__(self, coordinates):
        self.coordinates = coordinates

        self.SiPM_angles = np.array([-4.375, -3.125, -1.875, -0.625, 0.625, 1.875, 3.125, 4.375])
        self.SiPM_radii = np.array([1554.19, 1588.47, 1623.515, 1659.325, 1695.93, 1733.33, 1771.56, 1810.635])
        self.SiPM_channels = [69, 71, 65, 67, 60, 62, 56, 58, 68, 70, 64, 66, 59, 61, 55, 57, 41, 43, 37, 39, 50, 52,
                            46, 48, 40, 42, 36, 38, 49, 51, 45, 47, 20, 22, 33, 35, 29, 31, 24, 26, 19, 21, 32, 34,
                            28, 30, 23, 25, 14, 16, 10, 12, 1, 3, 5, 7, 13, 15, 9, 11, 0, 2, 4, 6]

        self.Tile_h = np.array([34.28, 34.28, 35.18, 35.18, 37.40, 37.40, 39.07, 39.07])
        self.Tile_a = np.array([33.53, 33.53, 35.03, 35.03, 36.59, 36.59, 37.41, 37.41])
        self.Tile_b = np.array([34.28, 34.28, 35.81, 35.81, 36.80, 36.80, 38.47, 38.47])

        self.Board_angles = np.array([-5, 5])
        self.Board_radii = np.array([1537.05, 1537.05 + 292.5])


    def GetChannelByPosition(self, x, y):
        """
        Calculates if a given point (x, y) lies on a tile of the tileboard and
        returns the channel number.

        Args:
            x, y (float): Cartesian coordinates.

        Returns:
            A channel number if (x, y) is within a tile, or
            -1 if (x, y) is on the tileboard but between two tiles, or
            -2 if (x, y) is outside the tileboard,
        """
        r, phi = self.coordinates.CartesianToPolar(x, y)
        if phi < self.Board_angles[0] or phi > self.Board_angles[1] or r < self.Board_radii[0] or r > self.Board_radii[1]:
            return -2

        slice_fraction = 5 / 4.
        slice_index = int((phi + 5) / slice_fraction)
        phi_rest = phi - slice_fraction/2 - (slice_index - 4) * slice_fraction

        # Use the symmetry
        phi_rest = -np.abs(phi_rest)
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

        return -1


    def DrawOutline(self, ax, detail=30):
        """
        Draws the outline of the tileboard.

        Args:
            ax: The pyplot axis to draw to.
            detail (int): Number of points used to draw the arcs.
        """
        r1 = self.Board_radii[0]
        r2 = self.Board_radii[1]
        theta1 = self.Board_angles[0]
        theta2 = self.Board_angles[1]

        ax.plot(*self.coordinates.PolarToCartesian(self.Board_radii, np.full(2, self.Board_angles[0])), color="k")
        ax.plot(*self.coordinates.PolarToCartesian(self.Board_radii, np.full(2, self.Board_angles[1])), color="k")
        ax.plot(*self.coordinates.PolarToCartesian(np.full(detail, r1), np.linspace(*self.Board_angles, detail)), color="k")
        ax.plot(*self.coordinates.PolarToCartesian(np.full(detail, r2), np.linspace(*self.Board_angles, detail)), color="k")

    def DrawSiPMs(self, ax, label_pos=False, radii=None, angles=None, format_str="bo"):
        """
        Draws SiPM positions.

        Args:
            ax: The pyplot axis to draw to.
            label_pos (bool): If True, channel labels also show the cartesian
                positions. Default is False.
            radii (np.array): If None specified (which is the default), then
                the SiPM positions of the tileboard are used.
            angles (np.array): If None specified (which is the default), then
                the SiPM positions of the tileboard are used.
            format_str (string): Default is "bo".
        """
        x = []
        y = []
        i = 0
        for r in (self.SiPM_radii if radii is None else radii):
            for phi in (self.SiPM_angles if angles is None else angles):
                xi, yi = self.coordinates.PolarToCartesian(r, phi)
                x.append(xi)
                y.append(yi)
                label = "{}".format(self.SiPM_channels[i])
                if label_pos:
                    label += "\n({:.2f}, {:.2f})".format(xi, yi)
                ax.text(xi, yi, label)
                i += 1

        ax.plot(x, y, format_str)

    def DrawTiles(self, ax):
        """
        Draw the outlines of the scintillator tiles on the tileboard.
        Args:
            ax: The pyplot axis to draw to.
        """
        for r, h, a, b in zip(self.SiPM_radii, self.Tile_h, self.Tile_a, self.Tile_b):
            x = np.array([-a/2, a/2, b/2, -b/2])
            y = np.array([-h/2, -h/2, h/2, h/2])
            for phi in self.SiPM_angles:
                x1, y1 = self.coordinates.Rotate(x, y, phi - 90 + self.coordinates.base_rotation)
                x1, y1 = self.coordinates.Transform(x1, y1, r, phi)
                ax.add_patch(patches.Polygon(xy=list(zip(x1, y1)), facecolor="c", alpha=0.3, edgecolor="b"))