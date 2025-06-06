import pandas as pd
import numpy as np
from .utils import boundary_raw2mat, boundary_raw2mat_single_rc

class PlotBoundary:
    def __init__(self, csv_filepath, mode="raw2mat", row=None, col=None):
        self.csv_filepath = csv_filepath
        self.mode = mode
        self.row = row
        self.col = col
        self.boundary_arr = None
        if mode == "raw2mat":
            if row is None or col is None:
                raise ValueError("Row and column must be specified for raw2mat mode.")
            self.boundary_arr = boundary_raw2mat(csv_filepath, row, col)
        elif mode == "raw2mat_single_rc":
            self.boundary_arr = boundary_raw2mat_single_rc(csv_filepath)
        else:
            raise ValueError("Unsupported mode. Use 'raw2mat' or 'raw2mat_single_rc'.")

    def file_sanity_check(self):
        # TODO:add sanity check for the file
        raise NotImplementedError("File sanity check is not implemented yet.")

    def get_field_points(self):
        if self.boundary_arr is None:
            raise ValueError("Boundary array is not initialized.")
        return self.boundary_arr
    
    def __getitem__(self, key):
        if self.boundary_arr is None:
            raise ValueError("Boundary array is not initialized.")
        return self.boundary_arr[key]