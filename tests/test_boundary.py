import pytest
import os
from task_planner.plot_boundary import PlotBoundary

def test_boundary_file_read():
    # Define the path to the test file
    test_file_path = os.path.join("tests", "boundary_files", "single_rc.csv")

    # Ensure the file exists
    assert os.path.exists(test_file_path), f"Test file {test_file_path} does not exist."

    # Initialize the PlotBoundary object
    plot_boundary = PlotBoundary(csv_filepath=test_file_path, mode="raw2mat_single_rc")

    # Check that the boundary array is not None
    assert plot_boundary.boundary_arr is not None, "Boundary array should not be None."

    # Check the shape of the boundary array
    assert len(plot_boundary.boundary_arr.shape) == 4, "Boundary array should be a 4D array."

    # Check that the array contains the expected number of rows and columns
    n_rows, n_cols, _, _ = plot_boundary.boundary_arr.shape
    assert n_rows > 0 and n_cols > 0, "Boundary array should have rows and columns."

    # Check that the array contains valid latitude and longitude values
    for row in plot_boundary.boundary_arr:
        for plot in row:
            for point in plot:
                lat, lon = point
                assert -90 <= lat <= 90, f"Invalid latitude value: {lat}"
                assert -180 <= lon <= 180, f"Invalid longitude value: {lon}"