import numpy as np
import pandas as pd
import re

def dms2dec(dms_str):
    """Return decimal representation from any DMS format.
    
    >>> dms2dec(utf8(48°53'10.18"N))
    48.8866111111F
    
    >>> dms2dec(utf8(2°20'35.09"E))
    2.34330555556F
    
    >>> dms2dec(utf8(48°53'10.18"S))
    -48.8866111111F
    
    >>> dms2dec(utf8(2°20'35.09"W))
    -2.34330555556F
    
    """
    
    dms_str = re.sub(r'\s', '', dms_str)
    
    sign = -1 if re.search('[swSW]', dms_str) else 1
    # Match numbers including optional decimal part, but only split on DMS symbols, not decimal points
    numbers = re.findall(r'\d+(?:\.\d+)?', dms_str)

    degree = numbers[0]
    minute = numbers[1] if len(numbers) >= 2 else '0'
    second = numbers[2] if len(numbers) >= 3 else '0'

    return sign * (float(degree) + float(minute) / 60 + float(second) / 3600)


def boundary2waypoint(boundary, n_pts=(1, 1)):
    """
    Generate a grid of points within the boundary.

    Args:
        boundary (numpy.ndarray): Array of four points defining the boundary.
        n_pts (tuple): A tuple (y, x) specifying the number of points along the x and y axes.

    Returns:
        numpy.ndarray: A 2D grid of points as numpy arrays.
    """
    y_pts, x_pts = n_pts


    # Calculate the vectors along the edges
    left_vector = boundary[2] - boundary[0]
    right_vector = boundary[3] - boundary[1]

    # Generate the grid of points
    grid_points = []
    for i in range(y_pts):
        row_points = []
        left_interp = boundary[0] + left_vector * (i + 1) / (y_pts + 1)
        right_interp = boundary[1] + right_vector * (i + 1) / (y_pts + 1)
        row_vector = right_interp - left_interp
        for j in range(x_pts):
            point = left_interp + row_vector * (j + 1) / (x_pts + 1)
            row_points.append(point)
        grid_points.append(row_points)
    # OPTIMIZE: use gridmesh to generate the grid points
    # for i in range(y_pts):
    #     row_points = []
    #     top_interp = boundary[0] + top_vector * (i + 1) / (y_pts + 1)
    #     bot_interp = boundary[2] + bot_vector * (i + 1) / (y_pts + 1)
    #     row_vector = bot_interp - top_interp
    #     for j in range(x_pts):
    #         point = top_interp + row_vector * (j + 1) / (x_pts + 1)
    #         row_points.append(point)
    #     grid_points.append(row_points)

    return np.array(grid_points)

def zone_to_indices(col, row, total_col):
    # order of points for plot
    # 0--1
    # |  |
    # 2--3
    index = row * total_col*4 + col * 2
    ind_p1 = index
    ind_p2 = ind_p1 + 1
    ind_p3 = index + 2 * total_col 
    ind_p4 = ind_p3 + 1
    return [ind_p1, ind_p2, ind_p3, ind_p4]

def check_latlon_format(s):
    """
    Check if the string is in DMS format.
    """
    

def boundary_raw2mat(csv_filepath, row, col):
    # read csv
    df = pd.read_csv(csv_filepath, comment='#')  
    df['LATITUDE'] = df['LATITUDE'].apply(dms2dec)
    df['LONGITUDE'] = df['LONGITUDE'].apply(dms2dec)
    points_list = []
    for r in range(row):
        for c in range(col):
            indices = zone_to_indices(c, r, col)
            lat_lon = df.iloc[indices][['LATITUDE', 'LONGITUDE']].values
            points_list.append(lat_lon)
    # points_matrix_list = [np.array(points) for points in points_list]
    boundary_arr = np.array(points_list).reshape(row, col , 4, 2)
    return boundary_arr

def boundary_raw2mat_single_rc(csv_filepath, downsample_factor=None):
    df = pd.read_csv(csv_filepath)
    if downsample_factor is not None:
        from .grid_preprocessing import grid_downsample
        df = grid_downsample(df, downsample_factor)
    if df['LATITUDE'].dtype == object:
        df['LATITUDE'] = df['LATITUDE'].apply(dms2dec)
    if df['LONGITUDE'].dtype == object:
        df['LONGITUDE'] = df['LONGITUDE'].apply(dms2dec)
    horiz_pts = df[df['LABEL']=='HP'].sort_index().reset_index(drop=True)
    verti_pts = df[df['LABEL']=='VP'].sort_index().reset_index(drop=True)
    horiz_list = [horiz_pts.copy()]
    for pts in verti_pts[1:].iterrows():
        x_diff = pts[1]['X'] - verti_pts.iloc[0]['X']
        y_diff = pts[1]['Y'] - verti_pts.iloc[0]['Y']
        lat_diff = pts[1]['LATITUDE'] - verti_pts.iloc[0]['LATITUDE']
        lon_diff = pts[1]['LONGITUDE'] - verti_pts.iloc[0]['LONGITUDE']
        new_horiz = horiz_pts.copy()
        new_horiz['X'] += x_diff
        new_horiz['Y'] += y_diff
        new_horiz['LATITUDE'] += lat_diff
        new_horiz['LONGITUDE'] += lon_diff
        horiz_list.append(new_horiz)
    pts_grid_df = pd.concat(horiz_list)
    assert len(df[df['LABEL']=='VP'])%2 == 0, ValueError('Number of VP (vertial pts) points must be even')
    assert len(df[df['LABEL']=='HP'])%2 == 0, ValueError('Number of HP (horizontal pts) points must be even')
    n_rows = int(len(df[df['LABEL']=='VP'])/2) 
    n_cols = int(len(df[df['LABEL']=='HP'])/2) 
    points_list = []
    for r in range(n_rows):
        for c in range(n_cols):
            indices = zone_to_indices(c, r, n_cols)
            lat_lon = pts_grid_df.iloc[indices][['LATITUDE', 'LONGITUDE']].values
            points_list.append(lat_lon)
    # points_matrix_list = [np.array(points) for points in points_list]
    boundary_arr = np.array(points_list).reshape(n_rows, n_cols , 4, 2)
    return boundary_arr


def parse_config(config_str):
    config = config_str
    mission_name = config['mission_name']
    if 'color_chart' in config:
        color_chart_coord = (config['color_chart']['coord']['latitude'], config['color_chart']['coord']['longitude'], config['color_chart']['coord']['altitude'])
    else:
        color_chart_coord = None
    plot_path = config['plot']['file_path']
    plot_mode = config['plot']['def_type']
    if plot_mode == "all":
        plot_mode = "raw2mat"
    if plot_mode == "single_rc":
        plot_mode = "raw2mat_single_rc"
    if plot_mode == "raw2mat":
        plot_n_row = config['plot']['row']
        plot_n_col = config['plot']['column']
    else:
        plot_n_row = None
        plot_n_col = None
    suvery_r = config['suvery_cfg']['sample_size']['r']
    suvery_c = config['suvery_cfg']['sample_size']['c']
    suvery_height = config['suvery_cfg']['suvery_height']
    gimbal_angle_relative_to_line = 0 if 'gimbal_angle_relative_to_line' not in config['suvery_cfg'] else config['suvery_cfg']['gimbal_angle_relative_to_line']
    line_per_mission = None if 'line_per_mission' not in config['suvery_cfg'] else config['suvery_cfg']['line_per_mission']
    return {
        'mission_name': mission_name,
        'color_chart_coord': color_chart_coord,
        'plot_path': plot_path,
        'plot_mode': plot_mode,
        'plot_n_row': plot_n_row,
        'plot_n_col': plot_n_col,
        'suvery_r': suvery_r,
        'suvery_c': suvery_c,
        'suvery_height': suvery_height,
        'gimbal_angle_relative_to_line': gimbal_angle_relative_to_line,
        'line_per_mission': line_per_mission
    }