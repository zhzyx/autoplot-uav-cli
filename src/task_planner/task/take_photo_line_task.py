from .task import BaseTask
from ...kml.placemark import Placemark
from ...kml.action_group import ActionGroup
from ...kml.action import TakePhotoAction, GimbalRotateAction, HoverAction, RotateYawAction
from ...kml.waypoint_turn_param import WaypointTurnParam
from ...kml.waypoint_heading_param import WaypointHeadingParam
import pyproj # pyproj use longitude, latitude order default

class TakePhotoLineTask(BaseTask):
    '''
    Take photo line task, which is a line of waypoints with (optional non-stop) take photo action
    Process:
    1. reach the first waypoint
    2. correct the heading to the final point
    3. adjust the gimbal yaw angle to the correct angle
    4. take the first photo
    5. move to the next waypoint, take photo non stop
    6. repeat till the final point
    '''
    def __init__(self, locations, file_suffix, height, start_index=0, non_stop=False, speed=1, heading_angle=None, gimbal_yaw_relative_mode='line', gimbal_yaw_angle=0.0, gimbal_pitch_angle=-90, shutter_early_offset=0.):
        '''
        parameters:
        locations: list of locations, each location is a tuple of (lat, lon)
        file_suffix: file suffix for the photo, can be None, a string or a list of strings, if list, the length must be the same as locations
        non_stop: if True, take photo non stop, else stop then take photo
        speed: speed of the drone, if None, use the default speed
        heading_angle: heading angle of the drone, if None, compute the angle between the first and last location
        gimbal_yaw_relative_mode: gimbal yaw relative mode, if 'line', the gimbal yaw angle is relative to the line, if 'absolute', the gimbal yaw angle is absolute to the north
        gimbal_yaw_angle: gimbal yaw angle, if not None, adjust the gimbal yaw angle before the line start
        gimbal_pitch_angle: gimbal pitch angle, if not None, adjust the gimbal pitch angle before the line start
        shutter_early_offset: offset time for the shutter, in seconds, default is 0.0, if set, the photo will be taken shutter_early_offset seconds before the waypoint.
            since the commnand and the actual shutter time may have some delay,  if we use non_stop, the photo may be taken after the waypoint.
            this param is used to adjust the waypoint based on the speed of the drone. to make sure the photo is taken at the right position.
        '''
        super().__init__(start_index)
        self._locations = locations
        self._file_suffix = file_suffix
        self._height = height
        self._start_index = start_index
        self._non_stop = non_stop
        self._gimbal_yaw_relative_mode = gimbal_yaw_relative_mode
        self._gimbal_yaw_angle = gimbal_yaw_angle
        self._gimbal_pitch_angle = gimbal_pitch_angle
        self._speed = speed
        self._use_global_speed = (speed is None)
        self._heading_angle = heading_angle
        self._shutter_early_offset = shutter_early_offset
        self._acutal_gimbal_yaw_angle = self.compute_acutal_gimbal_yaw_angle()
        if self._shutter_early_offset < 0:
            raise ValueError("shutter_early_offset must be non-negative")
        if len(locations) < 2:
            raise ValueError("At least two locations are required for a line task")
        if isinstance(file_suffix, str):
            file_suffix = [file_suffix] * len(locations)
        elif len(file_suffix) != len(locations):
            raise ValueError("file_suffixes must have the same length as locations or be a single string")
        # if heading_angle is None,
        # set the heading angle to the angle between the first and last location
        if heading_angle is None:
            #TODO: This seems return the othogonal angle, need to check the pyproj inv function
            geod = pyproj.Geod(ellps='WGS84')
            heading_angle, _, _ = geod.inv(locations[0][1], locations[0][0], locations[-1][1], locations[-1][0])
            self._heading_angle = heading_angle % 360
            if self._heading_angle > 180:
                self._heading_angle -= 360
        # TODO check how offline the points are, if too far, warn the user
        self._create_init_placemarks()
        
    def compute_acutal_gimbal_yaw_angle(self):
        if self._gimbal_yaw_angle is None:
            return None
        if self._gimbal_yaw_relative_mode == 'line':
            # compute the gimbal yaw angle based on the line direction
            geod = pyproj.Geod(ellps='WGS84')
            az, _, _ = geod.inv(self._locations[0][1], self._locations[0][0], self._locations[-1][1], self._locations[-1][0])
            actual_yaw = (az + self._gimbal_yaw_angle) % 360
            if actual_yaw > 180:
                actual_yaw -= 360
            return actual_yaw 
        elif self._gimbal_yaw_relative_mode == 'absolute':
            actual_yaw = self._gimbal_yaw_angle % 360
            if actual_yaw > 180:
                actual_yaw -= 360
            return actual_yaw
        else:
            raise ValueError("gimbal_yaw_relative_mode must be 'line' or 'absolute'")
        
    def _create_init_placemarks(self):
        heading_param = WaypointHeadingParam(
                heading_mode='fixed',
            )
        # create the first action
        first_placemark_actions = []
        # rotate the drone to the heading angle if set
        if self._heading_angle is not None:
            rotate_yaw_action = RotateYawAction(action_id=0, aircraft_heading=self._heading_angle)
            first_placemark_actions.append(rotate_yaw_action)
        # rotate the gimbal to the gimbal yaw angle if set
        # NOTE: DJI Pilot 2.0 does not support rotate gimbal and yaw at the same time, so we need to separate them
        # if self._acutal_gimbal_yaw_angle is not None or self._gimbal_pitch_angle is not None:
        #     rotate_action = GimbalRotateAction(action_id=0, 
        #                                        gimbal_yaw_rotate_enable=(self._gimbal_yaw_angle is not None),
        #                                        gimbal_yaw_rotate_angle=self._gimbal_yaw_angle, 
        #                                        gimbal_pitch_rotate_enable=(self._gimbal_pitch_angle is not None),
        #                                        gimbal_pitch_rotate_angle=self._gimbal_pitch_angle)
        if self._acutal_gimbal_yaw_angle is not None:
            rotate_action = GimbalRotateAction(action_id=0, gimbal_yaw_rotate_enable=True, gimbal_yaw_rotate_angle=self._acutal_gimbal_yaw_angle)
            first_placemark_actions.append(rotate_action)
        if self._gimbal_pitch_angle is not None:
            rotate_action = GimbalRotateAction(action_id=0, 
                                               gimbal_pitch_rotate_enable=True,
                                               gimbal_pitch_rotate_angle=self._gimbal_pitch_angle)
            first_placemark_actions.append(rotate_action)
        # for start of the line, hover for 1 seconds before taking photo
        # hover_action = HoverAction(action_id=0, hover_time=1)
        # first_placemark_actions.append(hover_action)
        take_photo_action = TakePhotoAction(action_id=0,
                                            file_suffix=self._file_suffix[0])
        first_placemark_actions.append(take_photo_action)
        action_group = ActionGroup(group_id=self._start_index, actions=first_placemark_actions)
        first_placemark = Placemark(
            coordinates=self._locations[0],
            index=self._start_index, 
            ellipsoid_height=self._height, 
            height=self._height,
            waypoint_speed=self._speed,
            waypoint_turn_param=WaypointTurnParam(
                turn_mode='toPointAndStopWithDiscontinuityCurvature',
            ), # for the first waypoint, direct go to the point and stop
            waypoint_heading_param=heading_param,
            action_group=action_group,
            use_global_height=False, 
            use_global_speed=self._use_global_speed,
            use_global_turn_param=False,
            use_straight_line=False
        )
        self._placemarks.append(first_placemark)
        # create the rest of the placemarks
        # if non_stop set turn mode to 'toPointAndPassWithContinuityCurvature' and damping_dist to 0
        turn_param = None
        if self._non_stop:
            turn_param = WaypointTurnParam(turn_mode='toPointAndPassWithContinuityCurvature', damping_dist=0) 

        for i, (loc, file_suffix) in enumerate(zip(self._locations[1:-1], self._file_suffix[1:-1]), start=1):
            take_photo_action = TakePhotoAction(action_id=0,
                                                file_suffix=file_suffix)
            action_group = ActionGroup(group_id=self._start_index + i, actions=[take_photo_action])
            if self._shutter_early_offset != 0:
                offset_distance = self._shutter_early_offset * self._speed # in meter
                geod = pyproj.Geod(ellps='WGS84')
                offset_az, _, offset_max_dist = geod.inv(loc[1], loc[0], self._locations[i-1][1], self._locations[i-1][0])
                if offset_max_dist < offset_distance:
                    raise ValueError(f"shutter_early_offset is too large, the distance between the two waypoints ({offset_max_dist}) is too small compare to the offset distance ({offset_distance})")
                lon, lat, _ = geod.fwd(loc[1], loc[0], offset_az, offset_distance)
                loc = (lat, lon)
            placemark = Placemark(
                coordinates=loc,
                index=self._start_index + i, 
                ellipsoid_height=self._height, 
                height=self._height,
                waypoint_speed=self._speed, 
                waypoint_heading_param=heading_param, 
                action_group=action_group,
                waypoint_turn_param=turn_param, 
                use_global_height=False, 
                use_global_speed=self._use_global_speed,
                use_global_heading_param=False, 
                use_global_turn_param=(turn_param is None),
                use_straight_line=False
            )
            self._placemarks.append(placemark)
        # Create the last placemark
        final_id = self._start_index + len(self._locations)-1
        # final_hover_action = HoverAction(action_id=0, hover_time=1)
        final_take_photo_action = TakePhotoAction(action_id=0, 
                                                  file_suffix=self._file_suffix[-1])
        final_action_group = ActionGroup(group_id=final_id, actions=[final_take_photo_action])
        placemark = Placemark(
            coordinates=self._locations[-1],
            index=final_id, 
            ellipsoid_height=self._height, 
            height=self._height,
            waypoint_speed=self._speed, 
            waypoint_heading_param=heading_param, 
            action_group=final_action_group,
            waypoint_turn_param=WaypointTurnParam(turn_mode='toPointAndStopWithDiscontinuityCurvature', damping_dist=0), # for the last, stop and take photo
            use_global_height=False,
            use_global_speed=self._use_global_speed,
            use_global_turn_param=False,
            use_straight_line=False,
            use_global_heading_param=False
        )
        self._placemarks.append(placemark)
