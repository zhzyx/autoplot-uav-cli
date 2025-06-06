import xmltodict

# Add a list of valid turn modes
VALID_TURN_MODES = [
    "coordinateTurn",
    "toPointAndStopWithDiscontinuityCurvature",
    "toPointAndStopWithContinuityCurvature",
    "toPointAndPassWithContinuityCurvature"
]

class WaypointTurnParam:
    """
    wpml:waypointTurnMode
        - Description: Defines the mode of waypoint turns.
        - Type: enum
        - Values:
            - coordinateTurn: Coordinated turns, no dips, early turns.
            - toPointAndStopWithDiscontinuityCurvature: Fly in a straight line and the aircraft stops at the point.
            - toPointAndStopWithContinuityCurvature: Fly in a curve and the aircraft stops at the point.
            - toPointAndPassWithContinuityCurvature: Fly in a curve and the aircraft will not stop at the point.
        - Note: For "Turns before waypoint. Flies through." mode in DJI Pilot2/FlightHub 2:
            1) Set "wpml:waypointTurnMode" to "toPointAndPassWithContinuityCurvature".
            2) Set "wpml:useStraightLine" to 1.
        - Required: Yes

    wpml:waypointTurnDampingDist
        - Description: Defines how far to the waypoint the aircraft should turn.
        - Type: float
        - Unit: m
        - Range: (0, maximum length of wayline segment]
        - Note: The wayline segment between two waypoints should be greater than the sum of the turn intercepts of two waypoints.
        - Required: Yes, if "wpml:waypointTurnMode" is "coordinateTurn" or "toPointAndPassWithContinuityCurvature" and "wpml:useStraightLine" is 1.

    """
    def __init__(self, turn_mode='coordinateTurn', damping_dist=0.0):
        if turn_mode not in VALID_TURN_MODES:
            raise ValueError(f"Invalid turn_mode. Must be one of {VALID_TURN_MODES}")
        self._turn_mode = turn_mode
        self._damping_dist = damping_dist

    # Getter and Setter for turn_mode
    @property
    def turn_mode(self):
        return self._turn_mode

    @turn_mode.setter
    def turn_mode(self, value):
        if value not in VALID_TURN_MODES:
            raise ValueError(f"Invalid turn_mode. Must be one of {VALID_TURN_MODES}")
        self._turn_mode = value

    # Getter and Setter for damping_dist
    @property
    def damping_dist(self):
        return self._damping_dist

    @damping_dist.setter
    def damping_dist(self, value):
        if value < 0:
            raise ValueError("damping_dist must be non-negative")
        self._damping_dist = value

    def to_dict(self):
        data = {
            "wpml:waypointTurnMode": self._turn_mode,
            "wpml:waypointTurnDampingDist": str(self._damping_dist)
        }
        return data

    def to_xml(self, is_global=True):
        data = {
            "wpml:waypointTurnParam": self.to_dict()
        }
        return xmltodict.unparse(data, pretty=True)

    @classmethod
    def from_xml(cls, xml_string):
        data = xmltodict.parse(xml_string)
        params = data.get("wpml:globalWaypointTurnParam", {})
        turn_mode = params.get("wpml:waypointTurnMode")
        damping_dist = float(params.get("wpml:waypointTurnDampingDist", 0.0))
        return cls(turn_mode, damping_dist)