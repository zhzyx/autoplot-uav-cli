import os
from ..task_planner.plot_boundary import PlotBoundary
from ..task_planner.plot_surveryor import PlotSurveyor
from .task import TakePhotoLineTask
from ..kml.kml import KML
import numpy as np

class GridPlotPlanner:
    def __init__(self, surveyor: PlotSurveyor, height: float = 10.0, speed: float = 1.0, 
                 non_stop=True, shutter_early_offset=0.5, gimbal_yaw=0.0,
                 mission_cfg=None, camera="P1"):
        """
        Initialize the Planner with a PlotSurveyor instance and output file.

        Args:
            surveyor (PlotSurveyor): An instance of PlotSurveyor to provide survey points.
            output_file (str): Path to the output KML file.
        """
        self.surveyor = surveyor
        self.height = height
        self.speed = speed
        self.non_stop = non_stop
        self.shutter_early_offset = shutter_early_offset
        self.gimbal_yaw = gimbal_yaw
        self.tasks = []
        self.pre_tasks = []
        self.post_tasks = []
        self.mission_cfg = mission_cfg
        self.camera = camera

    def add_pre_task(self, task):
        """
        Add a pre-task to the planner.

        Args:
            task (object): The pre-task to be added.
        """
        # TODO: adjust the start index of the task according to the number of pre-tasks
        self.pre_tasks.append(task)
        for t in self.tasks:
            t.start_index = t.start_index + 1
        for t in self.post_tasks:
            t.start_index = t.start_index + 1

    def pop_pre_task(self, index=None):
        """
        Remove a pre-task from the planner.

        Args:
            index (int): The index of the pre-task to be removed. If None, remove the last task.
        """
        if index is None:
            index = len(self.pre_tasks) - 1
        if index < 0 or index >= len(self.pre_tasks):
            raise IndexError("Index out of range")
        self.pre_tasks.pop(index)
        for t in self.pre_tasks:
            t.start_index = t.start_index - 1

        

    def plan_task(self, start_point='bl'):
        """
        Plan the task based on the surveyor data using a "back and forth" pattern starting from the bottom left.
        Args:
            start_point (str): The starting point of the task. Can be 'bl' (bottom left), 'br'(bottom right), 'tl' (top left), or 'tr' (top right).
        """
        survey_points = self.surveyor.get_survey_points()

        # convert survey points (r, c, x, y, 2) to (r*x, c*y, 2)
        r, c, x, y, _ = survey_points.shape
        survey_points = survey_points.transpose(0, 2, 1, 3, 4).reshape(r * x, c * y, 2)
        plot_rc = np.meshgrid(np.arange(r), np.arange(c), indexing='ij')
        plot_rc = np.array(plot_rc).transpose(1, 2, 0)
        plot_rc = np.repeat(plot_rc, x, axis=0)
        plot_rc = np.repeat(plot_rc, y, axis=1)

        if start_point == 'bl':
            pass
        elif start_point == 'tl':
            survey_points = np.rot90(survey_points, k=1)
            plot_rc = np.rot90(plot_rc, k=1)
        elif start_point == 'tr':
            survey_points = np.rot90(survey_points, k=2)
            plot_rc = np.rot90(plot_rc, k=2)
        elif start_point == 'br':
            survey_points = np.rot90(survey_points, k=3)
            plot_rc = np.rot90(plot_rc, k=3)

        # Create TakePhotoLineTask in a "back and forth" pattern, start from bottom left
        # IDEA: manipulate the survey points to control which side to start from

        direction = 1
        self.tasks = []
        for i in range(survey_points.shape[1]):
            if i == 0:
                line_init_hover_time = 5
            else:
                line_init_hover_time = 0
            locations = survey_points[:, i, :]
            if direction == 1:
                locations = locations[::-1]
            direction *= -1
            line_rc = plot_rc[:, i]
            file_suffix = [f"row-{line_rc[j, 0]+1}-col-{line_rc[j, 1]+1}" for j in range(survey_points.shape[0])]
            file_suffix = file_suffix[::-1] if direction == -1 else file_suffix
            locations = [(loc[0], loc[1]) for loc in locations]
            self.tasks.append(TakePhotoLineTask(locations=locations,
                                           start_index=i*len(file_suffix), 
                                           file_suffix=file_suffix, 
                                           height=self.height,
                                           speed=self.speed,
                                           gimbal_yaw_relative_mode='line',
                                           gimbal_yaw_angle=self.gimbal_yaw,
                                           non_stop=self.non_stop,
                                           shutter_early_offset=self.shutter_early_offset,
                                           init_hover_time=line_init_hover_time))
    
    def build_kml_obj(self):
        return KML(mission_config=self.mission_cfg, global_height=self.height, payload=self.camera)

    def create_kml(self):
        """
        Create a KML object and add the tasks to it.

        Returns:
            KML: The KML object containing the tasks.
        """
        kml = self.build_kml_obj()
        placemarks = []
        for task in self.pre_tasks:
            # Create a new placemark for each task
            placemarks.extend(task.placemarks)
        for task in self.tasks:
            # Create a new placemark for each task
            placemarks.extend(task.placemarks)
        for task in self.post_tasks:
            # Create a new placemark for each task
            placemarks.extend(task.placemarks)
        kml.placemarks = placemarks
        return kml
    
    def create_split_kml(self, num_tasks):
        """
        split the tasks into multiple KML objects.
        Args:
            num_tasks (int): The number of tasks in a single KML object.
        Returns:
            list of KML objects: The KML objects containing the tasks.
        """
        kml_list = []
        kml = self.build_kml_obj()
        placemarks = []
        placemarks_index = 0
        for task in self.pre_tasks:
            # Create a new placemark for each task
            placemarks.extend(task.placemarks)
        if len(self.pre_tasks) > 0:
            placemarks_index = self.pre_tasks[-1].end_index + 1

        for i, task in enumerate(self.tasks):
            # Create a new placemark for each task
            task.start_index = placemarks_index
            placemarks_index = task.end_index + 1
            placemarks.extend(task.placemarks)
            if (i + 1) % num_tasks == 0:
                kml.placemarks = placemarks
                kml_list.append(kml)
                kml = self.build_kml_obj()
                placemarks_index = 0
                placemarks = []
        for task in self.post_tasks:
            # Create a new placemark for each task
            placemarks.extend(task.placemarks)
        kml.placemarks = placemarks
        kml_list.append(kml)
        return kml_list

    def save_to_kml(self, file_path, split=False, num_tasks=10):
        """
        Save the waypoints to a KML file.

        Args:
            waypoints (list): List of Shapely Point objects representing waypoints.
        """
        if split:
            kml_list = self.create_split_kml(num_tasks)
            for i, kml in enumerate(kml_list):
                # Write to file
                folder_name = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.')[0])
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name, exist_ok=True)
                file_name = os.path.basename(file_path)
                with open(os.path.join(folder_name, f"{'.'.join(file_name.split('.')[:-1])}-part-{i}.kml"), "w") as f:
                    f.write(kml.to_xml())
        else:
            kml = self.build_kml_obj()
            # Write to file
            with open(file_path, "w") as f:
                f.write(kml.to_xml())
        
    def save_to_kmz(self, file_path, split=False, num_tasks=10):
        if split:
            kml_list = self.create_split_kml(num_tasks)
            for i, kml in enumerate(kml_list):
                # Write to file
                folder_name = os.path.join(os.path.dirname(file_path), os.path.basename(file_path).split('.')[0])
                if not os.path.exists(folder_name): 
                    os.makedirs(folder_name, exist_ok=True)
                file_name = os.path.basename(file_path)
                kml.to_kmz(os.path.join(folder_name,  f"{'.'.join(file_name.split('.')[:-1])}-part-{i}.kmz"))
        else:
            kml = self.build_kml_obj()
            # Write to file
            kml.to_kmz(file_path)