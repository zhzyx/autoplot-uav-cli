# Abstract action class for task planning
# each action may have sinlge or multiple task points, actions etc
# composed by a list of placemark
from ...kml.placemark import Placemark
from ...kml.action_group import ActionGroup
from ...kml.action import TakePhotoAction, GimbalRotateAction, HoverAction, RotateYawAction
from ...kml.waypoint_turn_param import WaypointTurnParam
from ...kml.waypoint_heading_param import WaypointHeadingParam
import pyproj # pyproj use longitude, latitude order default
class BaseTask:
    def __init__(self, start_index=0):
        self._start_index = start_index
        self._placemarks = []
    
    @property
    def start_index(self):
        return self._start_index
    
    @start_index.setter
    def start_index(self, value):
        if not isinstance(value, int):
            raise ValueError("start_index must be an integer")
        self._start_index = value
        self._update_placemark_index()
    
    @property
    def placemarks(self):
        return self._placemarks
    
    @placemarks.setter
    def placemarks(self, value):
        self._placemarks = value

    @property
    def end_index(self):
        '''
        return the end index of the task
        '''
        if len(self._placemarks) <= 0:
            return None
        return self._start_index + len(self._placemarks) - 1
    
    @end_index.setter
    def end_index(self, value):
        raise ValueError("end_index is read only")

    def _update_placemark_index(self):
        '''
        update the index of each placemark in the task
        '''
        for i, placemark in enumerate(self._placemarks):
            placemark.index = self._start_index + i
            # TODO: refactor this to the action_group class, where when update the group_id, it will update the start_index and end_index accordingly
            placemark.action_group.group_id = self._start_index + i
            placemark.action_group.start_index = self._start_index + i
            placemark.action_group.end_index = self._start_index + i
    


    
    

