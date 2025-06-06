import xmltodict


class WaypointHeadingParam:
    """
    wpml:waypointHeadingMode
        - Heading mode (enum):
            - followWayline: Along course direction. The nose of the aircraft follows the course direction to the next waypoint.
            - manually: The user can manually control the nose orientation of the aircraft during the flight to the next waypoint.
            - fixed: The nose of the aircraft maintains the yaw angle of the aircraft to the next waypoint after the waypoint action has been performed.
            - smoothTransition: Customized. The target yaw angle for a waypoint is given by "wpml:waypointHeadingAngle" and transitions evenly to the target yaw angle of the next waypoint during the flight segment.
            - towardPOI: The aircraft heading faces the point of interest.
        Required: Yes

    wpml:waypointHeadingAngle
        - Description: Yaw Angle of aircraft
        - Type: float
        - Unit: °
        - Range: [-180, 180]
        - Details: The target yaw angle for a given waypoint and a uniform transition to the target yaw angle for the next waypoint over the course of the flight segment.
        - Note: Required if "wpml:waypointHeadingMode" is "smoothTransition".
        Required: Yes

    wpml:waypointPoiPoint
        - Description: Point of interest
        - Type: Latitude, Longitude, Altitude
        - Details: When the wpml:waypointHeadingMode for a specific waypoint is set to "towardPOI", the aircraft's heading will face the point of interest while flying from that waypoint to the next waypoint.
        - Note: This field is only effective when wpml:waypointHeadingMode is set to "towardPOI". Currently, the Z-direction orientation towards the point of interest is not supported, so the altitude can be set to 0.
        - Note: Required if "wpml:waypointHeadingMode" is "towardPOI".
        Required: Yes

    wpml:waypointHeadingPathMode
        - Description: Direction of rotation of the aircraft yaw angle (enum):
            - clockwise
            - counterClockwise
            - followBadArc: Rotation of the aircraft yaw angle along the shortest path.
        Required: Yes
    """

    def __init__(self, heading_mode='followWayline', heading_angle=0, poi_point=(0., 0., 0.), heading_path_mode='followBadArc', poi_index=0):
        self.heading_mode = heading_mode
        self.heading_angle = heading_angle
        self.poi_point = poi_point
        self.heading_path_mode = heading_path_mode
        self.poi_index = poi_index

    # Getter and Setter for heading_mode
    @property
    def heading_mode(self):
        return self._heading_mode

    @heading_mode.setter
    def heading_mode(self, value):
        if value not in ['followWayline', 'manually', 'fixed', 'smoothTransition', 'towardPOI']:
            raise ValueError("heading_mode must be one of ['followWayline', 'manually', 'fixed', 'smoothTransition', 'towardPOI']")
        self._heading_mode = value

    # Getter and Setter for heading_angle
    @property
    def heading_angle(self):
        return self._heading_angle

    @heading_angle.setter
    def heading_angle(self, value):
        if not -180 <= value <= 180:
            raise ValueError("heading_angle must be in the range [-180, 180]")
        self._heading_angle = value

    # Getter and Setter for poi_point
    @property
    def poi_point(self):
        return self._poi_point

    @poi_point.setter
    def poi_point(self, value):
        if not isinstance(value, tuple) or len(value) != 3:
            raise ValueError("poi_point must be a tuple of (latitude, longitude, altitude)")
        self._poi_point = value

    # Getter and Setter for heading_path_mode
    @property
    def heading_path_mode(self):
        return self._heading_path_mode

    @heading_path_mode.setter
    def heading_path_mode(self, value):
        self._heading_path_mode = value

    # Getter and Setter for poi_index
    @property
    def poi_index(self):
        return self._poi_index

    @poi_index.setter
    def poi_index(self, value):
        self._poi_index = value

    def to_dict(self):
        data = {
            "wpml:waypointHeadingMode": self._heading_mode,
            "wpml:waypointHeadingAngle": str(self._heading_angle),
            "wpml:waypointPoiPoint": ",".join(map(str, self._poi_point)),
            "wpml:waypointHeadingPoiIndex": str(self._poi_index), # not sure if this is useful
        }
        if self._heading_path_mode:
            data["wpml:waypointHeadingPathMode"] = self._heading_path_mode
        return data

    def to_xml(self, is_global=True):
        if is_global:
            data = {
                "wpml:globalWaypointHeadingParam": self.to_dict()
            }
        else:
            data = {
                "wpml:waypointHeadingParam": self.to_dict()
            }
        return xmltodict.unparse(data, pretty=True)
    
    @classmethod
    def from_xml(cls, xml_string):
        data = xmltodict.parse(xml_string)
        params = data.get("wpml:globalWaypointHeadingParam", {})
        heading_mode = params.get("wpml:waypointHeadingMode")
        heading_angle = float(params.get("wpml:waypointHeadingAngle", 0))
        poi_point = tuple(map(float, params.get("wpml:waypointPoiPoint", "0.0,0.0,0.0").split(',')))
        poi_index = int(params.get("wpml:waypointHeadingPoiIndex", 0))
        return cls(heading_mode, heading_angle, poi_point, poi_index=poi_index)
