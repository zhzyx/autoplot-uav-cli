import xmltodict
import zipfile
from datetime import datetime
from copy import deepcopy
from .waypoint_heading_param import WaypointHeadingParam
from .mission_config import MissionConfig
from .placemark import Placemark
from enum import Enum

class WaypointTurnMode(str, Enum):
    COORDINATE_TURN = "coordinateTurn"
    TO_POINT_AND_STOP_WITH_DISCONTINUITY_CURVATURE = "toPointAndStopWithDiscontinuityCurvature"
    TO_POINT_AND_STOP_WITH_CONTINUITY_CURVATURE = "toPointAndStopWithContinuityCurvature"
    TO_POINT_AND_PASS_WITH_CONTINUITY_CURVATURE = "toPointAndPassWithContinuityCurvature"

    

class KML:
    """
    wpml:globalWaypointTurnMode
        Global Waypoint Type (Global Waypoint Turn Mode)
        string enumerate:
            - coordinateTurn: Coordinate turn, but point, turn ahead
            - toPointAndStopWithDiscontinuityCurvature: Fly in a straight line, the aircraft will stop at the point
            - toPointAndStopWithContinuityCurvature: Curve flight, the aircraft will stop at the point
            - toPointAndPassWithContinuityCurvature: Curve flight, the aircraft will not stop at the point
        required: yes

    wpml:globalUseStraightLine
        Whether the global segment trajectory is as close to a straight line as possible
        Boolean:
            - 0: The trajectory of the flight segment is a curve in the whole process
            - 1: The trajectory of the flight segment should be as close as possible to the line connecting the two points
        required: yes
        Note: Required if and only if "wpml:globalWaypointTurnMode" is set to "toPointAndStopWithContinuityCurvature" 
              or "toPointAndPassWithContinuityCurvature". If the Element of a waypoint is additionally defined, 
              the local definition will override the global definition.
        Note: Documentation says it is not for M300, but it is used in M300.

    wpml:gimbalPitchMode
        Gimbal Pitch Control Mode
        string enumerate:
            - manual: Manual control. When the aircraft is flying from one waypoint to the next, the user can manually 
                      control the pitch angle of the gimbal; if there is no user control, the gimbal pitch angle when 
                      flying away from the waypoint is maintained.
            - usePointSetting: Set according to each waypoint. When the aircraft flies from one waypoint to the next, 
                               the pitch angle of the gimbal transitions evenly to the pitch angle of the next waypoint.
        required: yes

    wpml:globalHeight
        Global height of flight route (related to the height of takeoff point)
        float
        unit: m
        required: yes
    NOTE: Since there are many fields in the XML that we dont care about, 
         we will not implement the from_xml method for now.
        They are hardcoded in the code. Those are left for future to implement.
    """
    def __init__(self, 
                 create_time=None,
                 update_time=None,
                 mission_config=None, 
                 global_waypoint_heading_param=None, 
                 global_waypoint_turn_mode="toPointAndPassWithContinuityCurvature",
                 gimbal_pitch_mode="manual",
                 global_height=5.0,
                 placemarks=None):
        current_datetime = datetime.now()
        if create_time is None:
            self._create_time = current_datetime
        else:
            if isinstance(create_time, (str, int)):
                self._create_time = datetime.fromtimestamp(float(create_time))
            elif isinstance(create_time, datetime):
                self._create_time = create_time
            else:
                raise ValueError("create_time must be a datetime object, string, or integer representing a timestamp.")
        if update_time is None:
            self._update_time = current_datetime
        else:
            if isinstance(update_time, (str, int)):
                self._update_time = datetime.fromtimestamp(float(update_time))
            elif isinstance(update_time, datetime):
                self._update_time = update_time
            else:
                raise ValueError("update_time must be a datetime object, string, or integer representing a timestamp.")
        self._mission_config = mission_config if mission_config else MissionConfig()
        # TODO: move this to new class WaypointHeadingParam
        self._global_waypoint_heading_param = global_waypoint_heading_param if global_waypoint_heading_param else WaypointHeadingParam()
        self._global_waypoint_turn_mode = global_waypoint_turn_mode
        self._gimbal_pitch_mode = gimbal_pitch_mode
        self._global_height = global_height
        if placemarks is None:
            self._placemarks = []
        else:
            if not isinstance(placemarks, list):
                raise TypeError("placemarks must be a list of Placemark objects.")
            for placemark in placemarks:
                if not isinstance(placemark, Placemark):
                    raise TypeError("Each placemark must be an instance of the Placemark class.")
            self._placemarks = placemarks

    @property
    def create_time(self):
        return self._create_time
    
    @property
    def update_time(self):
        return self._update_time
    
    @property
    def mission_config(self):
        return self._mission_config
    
    @property
    def placemarks(self):
        return self._placemarks
    
    @create_time.setter
    def create_time(self, value):
        self._create_time = value
    
    @update_time.setter
    def update_time(self, value):
        self._update_time = value

    @mission_config.setter
    def mission_config(self, value):
        self._mission_config = value

    @placemarks.setter
    def placemarks(self, value):
        if not isinstance(value, list):
            raise TypeError("placemarks must be a list of Placemark objects.")
        for placemark in value:
            if not isinstance(placemark, Placemark):
                raise TypeError("Each placemark must be an instance of the Placemark class.")
        self._placemarks = value

    def add_placemark(self, placemark):
        if not isinstance(placemark, Placemark):
            raise TypeError("placemark must be an instance of the Placemark class.")
        # TODO: support passing lat lon
        self._placemarks.append(placemark)

    def pop_placemark(self, index=None):
        if index is None:
            return self._placemarks.pop()
        else:
            if not isinstance(index, int):
                raise TypeError("index must be an integer.")
            if index < 0 or index >= len(self._placemarks):
                raise IndexError("Index out of range.")
            return self._placemarks.pop(index)

    
    def to_dict(self):
        data = {
            "kml": {
                "@xmlns": "http://www.opengis.net/kml/2.2",
                "@xmlns:wpml": "http://www.dji.com/wpmz/1.0.3",
                "Document": {
                    "wpml:createTime": str(int(self.create_time.timestamp())),
                    "wpml:updateTime": str(int(self.update_time.timestamp())),
                    "wpml:missionConfig": self.mission_config.to_dict(),
                    "Folder": {
                        "wpml:templateType": "waypoint",
                        "wpml:templateId": 0,
                        "wpml:waylineCoordinateSysParam": {
                            "wpml:coordinateMode": "WGS84",
                            "wpml:heightMode": "relativeToStartPoint",
                            "wpml:positioningType": "Custom" # probably need to change for other drones
                        },
                        "wpml:autoFlightSpeed": 1.0,
                        "wpml:globalHeight": self._global_height,
                        "wpml:caliFlightEnable": 0,
                        "wpml:gimbalPitchMode": self._gimbal_pitch_mode,
                        "wpml:globalWaypointHeadingParam": self._global_waypoint_heading_param.to_dict(),
                        "wpml:globalWaypointTurnMode": self._global_waypoint_turn_mode,
                        "wpml:globalUseStraightLine": 1,
                        "wpml:payloadParam": {
                            "wpml:payloadPositionIndex": 0,
                            "wpml:meteringMode": "average",
                            "wpml:dewarpingEnable": 0,
                            "wpml:returnMode": "singleReturnStrongest",
                            "wpml:samplingRate": 24000,
                            "wpml:focusMode": "firstPoint",
                            "wpml:scanningMode": "nonRepetitive",
                            "wpml:modelColoringEnable": 0
                        },
                        'Placemark': [p.to_dict() for p in self.placemarks]},
                }
            }
        }
        return data
    
    def to_xml(self):
        return xmltodict.unparse(self.to_dict(), pretty=True)
    
    def from_xml(self, xml_string):
        # TODO: Implement the from_xml method to parse XML data and populate the KMLTemplate object.
        # find a way to handle the "hardcoded" values in this class
        raise NotImplementedError("from_xml method is not implemented yet.")
    
    def save_xml(self, filename):
        with open(filename, 'w') as file:
            file.write(self.to_xml())

    def to_kmz(self, filename):
        """
        Save as KMZ file. 
        structure: 
        filename.kmz (zipped)
            wpmz/
                └── template.kml 
        """
        with zipfile.ZipFile(filename, 'w') as kmz:
            kmz.writestr('wpmz/template.kml', self.to_xml())