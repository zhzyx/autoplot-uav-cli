from .task import BaseTask
from ...kml.placemark import Placemark
from ...kml.action_group import ActionGroup
from ...kml.action import TakePhotoAction, GimbalRotateAction, HoverAction, RotateYawAction, FocusAction
from ...kml.waypoint_turn_param import WaypointTurnParam
from ...kml.waypoint_heading_param import WaypointHeadingParam


class TakePhotoTask(BaseTask):
    def __init__(self, location, file_suffix, height, 
                 start_index=0, non_stop=False, speed=3,
                 gimbal_yaw_angle=None, gimbal_pitch_angle=None,
                 turn_param=None, heading_param=None, focus=True):
        '''
        parameters:
        location: tuple of (lat, lon)
        file_suffix: file suffix for the photo, can be None, a string or a list of strings
        non_stop: if True, take photo non stop, else take photo once
        gimbal_yaw_angle: gimbal yaw angle, if None, use the default angle
        turn_param: turn parameter for the waypoint, can be None or WaypointTurnParam object, This param have the highest priority. if set, the non_stop will be ignored
        heading_param: heading parameter for the waypoint, can be None or WaypointHeadingParam object

        '''
        super().__init__(start_index)
        self._location = location
        self._file_suffix = file_suffix
        self._height = height
        self._start_index = start_index
        self._non_stop = non_stop
        if non_stop:
            self._turn_param = WaypointTurnParam(turn_mode='toPointAndPassWithContinuityCurvature', damping_dist=0)
        self.gimbal_yaw_angle = gimbal_yaw_angle
        self.gimbal_pitch_angle = gimbal_pitch_angle
        self._turn_param = turn_param
        self._heading_param = heading_param
        self._speed = speed
        self._focus = focus
        # init all the actions for the task
        self._create_init_placemarks()

    def _create_init_placemarks(self):
        adjust_actions = []
        if self.gimbal_yaw_angle is not None:
            rotate_action = GimbalRotateAction(action_id=0, gimbal_yaw_rotate_enable=True, gimbal_yaw_rotate_angle=self.gimbal_yaw_angle)
            # NOTE: the rotation is non blocking, so if no hover action is added, the drone will take photo while rotating
            adjust_actions.append(rotate_action)
        if self.gimbal_pitch_angle is not None:
            rotate_action = GimbalRotateAction(action_id=0, gimbal_pitch_rotate_enable=True, gimbal_pitch_rotate_angle=self.gimbal_pitch_angle)
            adjust_actions.append(rotate_action)
        if self. gimbal_pitch_angle is not None or self.gimbal_yaw_angle is not None:
            hover_action = HoverAction(hover_time=1)
            adjust_actions.append(hover_action)
        if self._focus:
            focus_action = FocusAction()
            adjust_actions.append(focus_action)
        take_photo_action = TakePhotoAction(file_suffix=self._file_suffix)
        action_group = ActionGroup(group_id=0, actions=[*adjust_actions, take_photo_action])
        self._placemarks = [
            Placemark(coordinates=self.location,
                      index=self._start_index, 
                      ellipsoid_height=self._height, 
                      height=self._height,
                      waypoint_speed=self._speed, 
                      waypoint_heading_param=self._heading_param, 
                      action_group=action_group,
                      waypoint_turn_param=self._turn_param, 
                      use_global_height=False, 
                      use_global_speed=False,
                      use_global_heading_param=(self._heading_param is not None), 
                      use_global_turn_param=(self._turn_param is not None),
                      use_straight_line=False)
        ]
        
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, tuple) or len(value) != 2:
            raise ValueError("location must be a tuple of (lon, lat)")
        self._location = value
        self.placemarks[0].coordinates = value

    @property
    def file_suffix(self):
        return self._file_suffix

    @file_suffix.setter
    def file_suffix(self, value):
        self._file_suffix = value
        self.placemarks[0].action_group.actions[-1].file_suffix = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("height must be a number")
        self._height = value
        self.placemarks[0].ellipsoid_height = value
        self.placemarks[0].height = value

    @property
    def gimbal_yaw_angle(self):
        return self._gimbal_yaw_angle

    @gimbal_yaw_angle.setter
    def gimbal_yaw_angle(self, value):
        self._gimbal_yaw_angle = value

    @property
    def turn_param(self):
        return self._turn_param

    @turn_param.setter
    def turn_param(self, value):
        self._turn_param = value
        self.placemarks[0].waypoint_turn_param = value

    @property
    def heading_param(self):
        return self._heading_param

    @heading_param.setter
    def heading_param(self, value):
        self._heading_param = value
        self.placemarks[0].waypoint_heading_param = value
