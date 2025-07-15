import pandas as pd
import pyproj
geod = pyproj.Geod(ellps="WGS84")
from dms2dec.dms_convert import dms2dec


def dec2dms(dec: float) -> str:
    """Convert decimal degrees to DMS format."""
    deg = int(abs(dec))
    min_float = (abs(dec) - deg) * 60
    minute = int(min_float)
    sec = (min_float - minute) * 60
    direction = 'N' if dec >= 0 else 'S'
    return f"{deg}° {minute:02d}' {sec:.4f}\" {direction}"

def get_latlon_from_row(row):
    return dms2dec(row['LATITUDE']), dms2dec(row['LONGITUDE'])

def add_dummy_lines(line_0, line_1, line_2):
    # new line_1 = line_2 + (line_1 - line_0)
    # new line_2 = line_2 + (line_2 - line_0)
    line_0_lat, line_0_lon = get_latlon_from_row(line_0)
    line_1_lat, line_1_lon = get_latlon_from_row(line_1)
    line_2_lat, line_2_lon = get_latlon_from_row(line_2)
    inv_az01, _, dist_01 = geod.inv(line_0_lon, line_0_lat, line_1_lon, line_1_lat)
    inv_az02, _, dist_02 = geod.inv(line_0_lon, line_0_lat, line_2_lon, line_2_lat)
    dummy_line_1_lon, dummy_line_1_lat, _ = geod.fwd(line_2_lon, line_2_lat, inv_az01, dist_01)
    dummy_line_2_lon, dummy_line_2_lat, _ = geod.fwd(line_2_lon, line_2_lat, inv_az02, dist_02)
    dummy_line_1_row = line_2.copy()
    dummy_line_1_row['LATITUDE'] = dec2dms(dummy_line_1_lat)
    dummy_line_1_row['LONGITUDE'] = dec2dms(dummy_line_1_lon)
    dummy_line_2_row = line_2.copy()
    dummy_line_2_row['LATITUDE'] = dec2dms(dummy_line_2_lat)
    dummy_line_2_row['LONGITUDE'] = dec2dms(dummy_line_2_lon)
    return dummy_line_1_row, dummy_line_2_row


def grid_downsample(df):
    hp_df = df[df['LABEL']=='HP'].reset_index(drop=True)
    vp_df = df[df['LABEL']=='VP'].reset_index(drop=True)
    # make sure the number of HP and VP is even
    if hp_df.shape[0] % 2 != 0:
        raise ValueError("Number of HP points must be even")
    if vp_df.shape[0] % 2 != 0:
        raise ValueError("Number of VP points must be even")
    hp_n_plots = hp_df.shape[0] // 2
    vp_n_plots = vp_df.shape[0] // 2
    if hp_n_plots % 2 != 0:
        # extend the HP points
        dummy_line_1, dummy_line_2 = add_dummy_lines(hp_df.iloc[-3], hp_df.iloc[-2], hp_df.iloc[-1])
        hp_df = pd.concat([hp_df, dummy_line_1.to_frame().T, dummy_line_2.to_frame().T], ignore_index=True)
    if vp_n_plots % 2 != 0:
        # extend the VP points
        dummy_line_1, dummy_line_2 = add_dummy_lines(vp_df.iloc[-3], vp_df.iloc[-2], vp_df.iloc[-1])
        vp_df = pd.concat([vp_df, dummy_line_1.to_frame().T, dummy_line_2.to_frame().T], ignore_index=True) 
    # downsample the HP points [0, 3, 4, 7, 8, 11, 12, ...]
    seleted_indices_0 = range(0, hp_df.shape[0], 4)
    selected_indices_1 = range(3, hp_df.shape[0], 4)
    selected_indices = [i for sublist in zip(seleted_indices_0, selected_indices_1) for i in sublist]
    hp_df = hp_df.iloc[selected_indices].reset_index(drop=True)
    # downsample the VP points [0, 3, 4, 7, 8, 11, 12, ...]
    seleted_indices_0 = range(0, vp_df.shape[0], 4)
    selected_indices_1 = range(3, vp_df.shape[0], 4)
    selected_indices = [i for sublist in zip(seleted_indices_0, selected_indices_1) for i in sublist]
    print(selected_indices)
    vp_df = vp_df.iloc[selected_indices].reset_index(drop=True)
    return pd.concat([hp_df, vp_df], ignore_index=True)

def grid_downsample(df, factor=(2, 2) ):
    """
    Downsample the grid points in the dataframe.
    The dataframe should have a 'LABEL' column with values 'HP' and 'VP'.
    :param df: DataFrame containing the grid points with 'LABEL', 'LATITUDE', and 'LONGITUDE' columns.
    :param factor: Tuple of two integers, the first one is the downsample factor for HP points,
                   and the second one is the downsample factor for VP points.
    """
    hp_factor = factor[0]
    vp_factor = factor[1]
    hp_df = df[df['LABEL']=='HP'].reset_index(drop=True)
    vp_df = df[df['LABEL']=='VP'].reset_index(drop=True)
    # make sure the number of HP and VP is even
    if hp_df.shape[0] % 2 != 0:
        raise ValueError("Number of HP points must be even")
    if vp_df.shape[0] % 2 != 0:
        raise ValueError("Number of VP points must be even")
    hp_n_plots = hp_df.shape[0] // 2
    vp_n_plots = vp_df.shape[0] // 2
    if hp_n_plots % hp_factor != 0:
        add_n = hp_factor - (hp_n_plots % hp_factor)
        if add_n == hp_factor:
            add_n = 0
        for _ in range(add_n):
        # extend the HP points
            dummy_line_1, dummy_line_2 = add_dummy_lines(hp_df.iloc[-3], hp_df.iloc[-2], hp_df.iloc[-1])
            hp_df = pd.concat([hp_df, dummy_line_1.to_frame().T, dummy_line_2.to_frame().T], ignore_index=True)
    if vp_n_plots % 2 != 0:
        add_n = vp_factor - (vp_n_plots % vp_factor)
        if add_n == vp_factor:
            add_n = 0
        for _ in range(add_n):
        # extend the VP points
            dummy_line_1, dummy_line_2 = add_dummy_lines(vp_df.iloc[-3], vp_df.iloc[-2], vp_df.iloc[-1])
            vp_df = pd.concat([vp_df, dummy_line_1.to_frame().T, dummy_line_2.to_frame().T], ignore_index=True) 
    # downsample the HP points [0, 3, 4, 7, 8, 11, 12, ...]
    seleted_indices_0 = range(0, hp_df.shape[0], 2 * hp_factor) # start points
    selected_indices_1 = range(2* hp_factor - 1 , hp_df.shape[0], 2 * hp_factor) # end points
    selected_indices = [i for sublist in zip(seleted_indices_0, selected_indices_1) for i in sublist]
    hp_df = hp_df.iloc[selected_indices].reset_index(drop=True)
    # downsample the VP points [0, 3, 4, 7, 8, 11, 12, ...]
    seleted_indices_0 = range(0, vp_df.shape[0], 2 * vp_factor) # start points
    selected_indices_1 = range(2* vp_factor - 1 , vp_df.shape[0], 2 * vp_factor) # end points
    selected_indices = [i for sublist in zip(seleted_indices_0, selected_indices_1) for i in sublist]
    vp_df = vp_df.iloc[selected_indices].reset_index(drop=True)
    return pd.concat([hp_df, vp_df], ignore_index=True)

