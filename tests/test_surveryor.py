import pytest
import numpy as np
from task_planner.plot_boundary import PlotBoundary
from task_planner.plot_surveryor import PlotSurveyor

def test_plot_surveyor():
    # Define the path to the test file
    test_file_path = "tests/boundary_files/single_rc.csv"

    # Initialize the PlotBoundary object
    plot_boundary = PlotBoundary(csv_filepath=test_file_path, mode="raw2mat_single_rc")

    # Initialize the PlotSurveyor object with a grid of 2x2 points
    surveyor = PlotSurveyor(plot_boundary, n_pts=(2, 2))

    # Get the survey points
    survey_points = surveyor.get_survey_points()

    # Check the shape of the survey points array
    assert survey_points.shape == (plot_boundary.boundary_arr.shape[0],
                                    plot_boundary.boundary_arr.shape[1],
                                    2, 2, 2), "Survey points array shape is incorrect."

    # Check that the survey points are within valid latitude and longitude ranges
    for row in survey_points:
        for col in row:
            for grid_row in col:
                for point in grid_row:
                    lat, lon = point
                    assert -90 <= lat <= 90, f"Invalid latitude value: {lat}"
                    assert -180 <= lon <= 180, f"Invalid longitude value: {lon}"