from .action_group import ActionGroup
import xmltodict

class Placemark:
    def __init__(self, coordinates, index, ellipsoid_height, height, 
                 waypoint_speed=None, 
                 use_global_heading_param=True, waypoint_heading_param=None, 
                 use_global_turn_param=True, waypoint_turn_param=None, 
                 action_group=None, 
                 use_global_height=True, use_global_speed=True, use_straight_line=False, 
                 gimbal_pitch_angle=None, **kwargs):
        '''
        Initialize a Placemark object.
        Args:
            coordinates (list): A list of two floats [latitude, longitude]. will convert to (lon, lat) when saving to KML file.
            index (int): The index of the waypoint.
            ellipsoid_height (float): The ellipsoid height of the waypoint.
            height (float): The height of the waypoint.
            waypoint_speed (float, optional): The speed of the waypoint. Default is None.
            use_global_heading_param (bool, optional): Whether to use global heading parameter. Default is True.
            waypoint_heading_param (WaypointHeadingParam, optional): The heading parameter for the waypoint. Default is None.
            action_group (ActionGroup, optional): The action group for the waypoint. Default is None.
            waypoint_turn_param (WaypointTurnParam, optional): The turn parameter for the waypoint. Default is None.
            use_global_height (bool, optional): Whether to use global height. Default is True.
            use_global_speed (bool, optional): Whether to use global speed. Default is True.
            use_straight_line (bool, optional): Whether to use straight line. Default is False.
            gimbal_pitch_angle (float, optional): The gimbal pitch angle. Default is None.
        '''

        if len(coordinates) != 2:
            raise ValueError("Coordinates must be a list of two floats [latitude, longitude].")
        self._coordinates = coordinates
        self._index = index
        self._ellipsoid_height = ellipsoid_height
        self._height = height
        self._waypoint_speed = waypoint_speed
        self._waypoint_heading_param = waypoint_heading_param
        self._action_group = action_group
        self._waypoint_turn_param = waypoint_turn_param
        self._use_global_height = use_global_height
        self._use_global_speed = use_global_speed
        self._use_global_heading_param = use_global_heading_param
        self._use_straight_line = use_straight_line
        self._gimbal_pitch_angle = gimbal_pitch_angle
        self._use_global_turn_param = use_global_turn_param

    @property
    def gimbal_pitch_angle(self):
        return self._gimbal_pitch_angle

    @gimbal_pitch_angle.setter
    def gimbal_pitch_angle(self, value):
        self._gimbal_pitch_angle = value

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("Coordinates must be a list or tuple of two floats [latitude, longitude].")
        self._coordinates = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def ellipsoid_height(self):
        return self._ellipsoid_height

    @ellipsoid_height.setter
    def ellipsoid_height(self, value):
        self._ellipsoid_height = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def waypoint_speed(self):
        return self._waypoint_speed

    @waypoint_speed.setter
    def waypoint_speed(self, value):
        self._waypoint_speed = value

    @property
    def waypoint_heading_param(self):
        return self._waypoint_heading_param

    @waypoint_heading_param.setter
    def waypoint_heading_param(self, value):
        self._waypoint_heading_param = value

    @property
    def action_group(self):
        return self._action_group

    @action_group.setter
    def action_group(self, value):
        self._action_group = value

    @property
    def waypoint_turn_param(self):
        return self._waypoint_turn_param

    @waypoint_turn_param.setter
    def waypoint_turn_param(self, value):
        self._waypoint_turn_param = value

    @property
    def use_global_height(self):
        return self._use_global_height

    @use_global_height.setter
    def use_global_height(self, value):
        self._use_global_height = value

    @property
    def use_global_speed(self):
        return self._use_global_speed

    @use_global_speed.setter
    def use_global_speed(self, value):
        self._use_global_speed = value

    @property
    def use_global_heading_param(self):
        return self._use_global_heading_param

    @use_global_heading_param.setter
    def use_global_heading_param(self, value):
        self._use_global_heading_param = value

    @property
    def use_straight_line(self):
        return self._use_straight_line

    @use_straight_line.setter
    def use_straight_line(self, value):
        self._use_straight_line = value

    @property
    def use_global_turn_param(self):
        return self._use_global_turn_param

    @use_global_turn_param.setter
    def use_global_turn_param(self, value):
        self._use_global_turn_param = value

    def update_attribute(self, key, value):
        self.to_xml()[f"wpml:{key}"] = value

    def to_dict(self):  
        return {
            "Point": {"coordinates": f"{self._coordinates[1]},{self._coordinates[0]}"}, # KML uses (lon, lat) format
            "wpml:index": self._index,
            "wpml:ellipsoidHeight": self._ellipsoid_height,
            "wpml:height": self._height,
            **({"wpml:waypointSpeed": self._waypoint_speed} if self._waypoint_speed is not None else {}),
            **({"wpml:waypointHeadingParam": self._waypoint_heading_param.to_dict()} if self._waypoint_heading_param else {}),
            **({"wpml:waypointTurnParam": self._waypoint_turn_param.to_dict()} if self._waypoint_turn_param else {}),
            "wpml:useGlobalHeight": str(int(self._use_global_height)),
            "wpml:useGlobalSpeed": str(int(self._use_global_speed)),
            "wpml:useGlobalHeadingParam": str(int(self._use_global_heading_param)),
            "wpml:useStraightLine": str(int(self._use_straight_line)),
            "wpml:useGlobalTurnParam": str(int(self._use_global_turn_param)),
            "wpml:gimbalPitchAngle": str(self._gimbal_pitch_angle) if self._gimbal_pitch_angle is not None else None,
            **({"wpml:actionGroup": self._action_group.to_dict()} if self._action_group else {})
        }

    def to_xml(self):
        return xmltodict.unparse({"Placemark": self.to_dict()}, pretty=True)

    @classmethod
    def from_xml(cls, xml_data):
        return cls(
            coordinates=xml_data["Point"]["coordinates"],
            index=xml_data["wpml:index"],
            ellipsoid_height=xml_data["wpml:ellipsoidHeight"],
            height=xml_data["wpml:height"],
            waypoint_speed=xml_data.get("wpml:waypointSpeed"),
            waypoint_heading_param=xml_data.get("wpml:waypointHeadingParam"),
            action_group=ActionGroup.from_dict(xml_data["wpml:actionGroup"]) if "wpml:actionGroup" in xml_data else None,
            waypoint_turn_param=xml_data.get("wpml:waypointTurnParam"),
            use_global_height=bool(int(xml_data["wpml:useGlobalHeight"])),
            use_global_speed=bool(int(xml_data["wpml:useGlobalSpeed"])),
            use_global_heading_param=bool(int(xml_data["wpml:useGlobalHeadingParam"])),
            use_straight_line=bool(int(xml_data["wpml:useStraightLine"])),
            use_global_turn_param=bool(int(xml_data["wpml:useGlobalTurnParam"]))
        )


