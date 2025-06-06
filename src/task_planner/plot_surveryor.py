import numpy as np
from .plot_boundary import PlotBoundary
from .utils import boundary2waypoint

class PlotSurveyor:
    def __init__(self, plot_boundary: PlotBoundary, n_pts=(1, 1)):
        """
        Initialize the PlotSurveyor with a PlotBoundary instance and number of points.

        Args:
            plot_boundary (PlotBoundary): An instance of PlotBoundary containing the boundary array.
            n_pts (tuple): A tuple (r, c) specifying the number of points inside a plot along the row axis and col axis.
        """
        self.plot_boundary = plot_boundary
        self.n_pts = n_pts

    def get_survey_points(self):
        """
        Generate survey points based on the PlotBoundary array.

        Returns:
            numpy.ndarray: A 3D array where the first two dimensions represent the point grid,
                           and the third dimension contains the longitude and latitude.
        """
        if self.plot_boundary.boundary_arr is None:
            raise ValueError("Boundary array is not initialized in the provided PlotBoundary instance.")

        rows, cols, _, _ = self.plot_boundary.boundary_arr.shape
        survey_points = np.empty((rows, cols, self.n_pts[0], self.n_pts[1], 2))

        for r in range(rows):
            for c in range(cols):
                plot = self.plot_boundary.boundary_arr[r, c]
                points = boundary2waypoint(plot, self.n_pts)
                survey_points[r, c] = points

        return survey_points
