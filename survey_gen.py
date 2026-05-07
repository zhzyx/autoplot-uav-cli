from src.task_planner.plot_boundary import PlotBoundary
from src.task_planner.plot_surveryor import PlotSurveyor
from src.task_planner.planner import GridPlotPlanner
import numpy as np
import matplotlib.pyplot as plt
import os, yaml
from src.kml.mission_config import MissionConfig, create_M300_drone_info, create_M350_drone_info, create_M400_drone_info
from argparse import ArgumentParser

# arg parser

def parse_args():
    parser = ArgumentParser(description="KML Planner for Grid Plotting")
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration YAML file')
    return parser.parse_args()

def generate_kml_from_config(config):
    with open(config, "r") as f:
        config = yaml.safe_load(f)
    # integrity check
    mission_name = config['mission_name']
    if 'color_chart' in config:
        color_chart_coord = (config['color_chart']['coord']['latitude'], config['color_chart']['coord']['longitude'], config['color_chart']['coord']['altitude'])
    else:
        color_chart_coord = None
    if 'mission_cfg' in config:
        take_off_height = config['mission_cfg'].get('take_off_height', 5)  # Default to 25 if not specified
        transit_speed = config['mission_cfg'].get('transit_speed', 5)  # Default to 15 if not specified
        finish_action = config['mission_cfg'].get('finish_action', 'goHome')  # Default to 'noAction' if not specified
        downsample_factor = config['suvery_cfg'].get('downsample_factor', None)  # Default to None if not specified
        drone_model = config['mission_cfg'].get('drone_model', 'M300')  # Default to 'M300' if not specified
        print(f"Mission Config - Take-off Height: {take_off_height}, Transit Speed: {transit_speed}, Finish Action: {finish_action}, Drone Model: {drone_model}, Gimbal Pitch: {gimbal_pitch}")
        gimbal_angle_relative_to_line = config['suvery_cfg'].get('gimbal_angle_relative_to_line', 0)  # Default to 0 if not specified
        print(f"Mission Config - Take-off Height: {take_off_height}, Transit Speed: {transit_speed}, Finish Action: {finish_action}, Drone Model: {drone_model}")
        if drone_model == 'M300':
            drone_info = create_M300_drone_info()
        if drone_model == 'M350':
            drone_info = create_M350_drone_info()
        elif drone_model == 'M400':
            drone_info = create_M400_drone_info()
        else:
            raise ValueError(f"Unsupported drone model: {drone_model}")
        mission_cfg = MissionConfig(
            take_off_security_height= take_off_height,
            global_transitional_speed= transit_speed,
            finish_action=finish_action,
            drone_info=drone_info
        )
    else:
        gimbal_angle_relative_to_line = 0
        mission_cfg = MissionConfig(take_off_security_height=5, global_transitional_speed=5, finish_action='goHome')
        downsample_factor = None
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
    gimbal_pitch = config['suvery_cfg'].get('gimbal_pitch', -90)  # Default to -90 if not specified/
    gimbal_angle_relative_to_line = config['suvery_cfg'].get('gimbal_angle_relative_to_line', 0)
    line_per_mission = config['suvery_cfg'].get('line_per_mission', None)
    camera = config['suvery_cfg'].get('camera', 'P1')
    # Initialize PlotBoundary
    # Initialize PlotBoundary
    # csv_filepath = 'tests/boundary_files/xinxiang_small_plot.csv'
    # plot_boundary = PlotBoundary(csv_filepath, mode='raw2mat', row=11, col=87)

    plot_boundary = PlotBoundary(plot_path, mode=plot_mode, row=plot_n_row, col=plot_n_col, downsample_factor=downsample_factor)
    # Generate Survey Points
    surveyor = PlotSurveyor(plot_boundary, n_pts=(suvery_r, suvery_c))
    survey_points = surveyor.get_survey_points()
    print('Survey Points Shape:', survey_points.shape)
    from src.task_planner.planner import GridPlotPlanner
    from importlib import reload
    import src.task_planner.planner as planner_module
    import src.kml.kml as kml_module
    from src.task_planner.task import TakePhotoTask
    reload(kml_module)
    reload(planner_module)

    planner = GridPlotPlanner(surveyor, height=suvery_height, gimbal_yaw=gimbal_angle_relative_to_line, gimbal_pitch=gimbal_pitch, mission_cfg=mission_cfg, camera=camera)
    planner.plan_task()#start_point='tl')
    if color_chart_coord is not None:
        calib_board_action = TakePhotoTask((color_chart_coord[0], color_chart_coord[1]), 'colorchart', color_chart_coord[2], gimbal_pitch_angle= -90, gimbal_yaw_angle=0)
        planner.add_pre_task(calib_board_action)

    # planner.save_to_kml(f'./output/{mission_name}.kml', split=(line_per_mission is not None), num_tasks=line_per_mission)
    planner.save_to_kmz(f'./output/{mission_name}.kmz', split=(line_per_mission is not None), num_tasks=line_per_mission)
    # save the coordinates of the placemarks to csv 
    kml = planner.create_kml()
    kml.mission_config.to_dict()
    coords = [p.coordinates for p in kml.placemarks]
    import pandas as pd
    df = pd.DataFrame(coords, columns=['latitude', 'longitude'])
    df.to_csv(f"./report/{config['mission_name']}_coords.csv", index=True)

    # Visualize Boundaries with Shapely and Survey Points
    from shapely.geometry import Polygon
    fig, ax = plt.subplots(figsize=(10, 20))
    is_first_plot = True
    for row, survey_row in zip(plot_boundary.boundary_arr, survey_points):
        for plot, survey_grid in zip(row, survey_row):
            # Create a Shapely polygon for the boundary
            patch = Polygon(plot[[0, 1, 3, 2], :])
            x, y = patch.exterior.xy
            if is_first_plot:
                color = 'green' # Use green for the first plot r0c0 / Top-left plot
                is_first_plot = False
            else:
                color = 'red'
            ax.plot(y, x, c=color)
            p = ax.fill(y, x, alpha=0.5, color=color)
    # Plot survey points with using coords from kml
    scatter = ax.scatter(df['longitude'], df['latitude'], c='blue', marker='x', label='Survey Points')
    for i in range(len(df) - 2): 
        x1, y1 = df.iloc[i]['longitude'], df.iloc[i]['latitude']
        x2, y2 = df.iloc[i+1]['longitude'], df.iloc[i+1]['latitude']
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = (x2 - x1) * 0.1, (y2 - y1) * 0.1
        ax.annotate('', xy=(mid_x + dx, mid_y + dy), xytext=(mid_x - dx, mid_y - dy),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=1.5, alpha=0.7))
        ax.plot([x1, x2], [y1, y2], 'b-', lw=1.5, alpha=0.7)

    plt.title('Plot Boundaries with Survey Points')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.axis('off')
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.legend([p[0], scatter], ['Plot', 'Survey Points'], loc='upper right')
    os.makedirs('./report', exist_ok=True)
    plt.savefig(f'./report/{mission_name}_boundaries_with_survey_points.png', dpi=300, bbox_inches='tight')


if __name__ == "__main__":
    config_file = parse_args().config
    generate_kml_from_config(config_file)