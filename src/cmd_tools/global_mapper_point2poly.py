# This script processes CSV files in a specified input folder, 
# converting groups of 4 rows into polygons and then back to points, 
# while also adding empty rows between groups. The processed files 
# are saved in a specified output folder with the same filenames.

import pandas as pd 
import os
import glob
import argparse
from shapely.geometry import Point, Polygon

def point_to_polygon(points):
    # check if polygon is valid order
    if len(points) < 3:
        raise ValueError("At least 3 points are required to form a polygon.")
    # Create polygon from points
    polygon = Polygon(points)
    if not polygon.is_valid:
        # reorder points based on convex hull
        polygon = polygon.convex_hull
    return polygon

def polygon_to_points(polygon):
    if not polygon.is_valid:
        raise ValueError("Invalid polygon geometry.")
    # Get the exterior coordinates of the polygon
    points = list(polygon.exterior.coords)
    return points


def process_csv_files(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get all csv files in the input folder
    csv_files = glob.glob(os.path.join(input_folder, '*.csv'))
    
    for csv_file in csv_files:
        # Read the csv file
        df = pd.read_csv(csv_file)
        # Process groups of 4 rows
        if 'LABEL' in df.columns:
            df['LABEL'] = df['LABEL'].astype('string')
        result_rows = []
        num_rows = len(df)
        
        for i in range(0, num_rows, 4):
            group = df.iloc[i:i+4].copy()
            
            # # Swap row 2 and row 3 (0-based within group)
            # if len(group) >= 4:
            #     group_list = group.values.tolist()
            #     group_list[2], group_list[3] = group_list[3], group_list[2]
            #     for row in group_list:
            #         result_rows.append(row)
            # else:
            #     for row in group.values.tolist():
            #         result_rows.append(row)
            # 
            
            poly = point_to_polygon(group[['LATITUDE', 'LONGITUDE']].values)
            points = polygon_to_points(poly)
            poly_point_list = []
            for idx, (lat, lon) in enumerate(points[:-1]):  # Exclude the last point which is the same as the first
                label = group['LABEL'].iloc[idx % len(group)]  # Cycle through labels if less than points
                poly_point_list.append([lat, lon, label])
            result_rows.extend(poly_point_list)
            
            # Add empty row after each group
            result_rows.append([None] * 3)
        
        # Create result dataframe
        result_df = pd.DataFrame(result_rows, columns=['LATITUDE', 'LONGITUDE', 'LABEL'])
        # Output to the output folder with the same filename
        output_path = os.path.join(output_folder, os.path.basename(csv_file))
        result_df.to_csv(output_path, index=False)
        print(f"Processed: {csv_file} -> {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process CSV files by swapping rows and adding empty rows.')
    parser.add_argument(
        '--input_folder', 
        help='Path to the input folder containing CSV files')
    parser.add_argument(
        '--output_folder', 
        help='Path to the output folder for processed CSV files')
    
    args = parser.parse_args()
    process_csv_files(args.input_folder, args.output_folder)