from .action import Action
import xmltodict

class RotateYawAction(Action):
    """
    RotateYawAction Parameters:
    - wpml:aircraftHeading (float): Drone target yaw angle (relative to geographic north).
        Range: [-180, 180] (degrees).
        0° is due north, 90° is due east, -90° is due west, -180°/180° is due south.
    - wpml:aircraftPathMode (enum): Yaw rotation mode of the drone.
        NOTE: Document says float, but the controller will floor it to int
        Options: "clockwise", "counterClockwise".
    """

    def __init__(self, action_id=0, aircraft_heading=0, aircraft_path_mode="clockwise"):
        self.aircraft_heading = aircraft_heading
        self.aircraft_path_mode = aircraft_path_mode
        super().__init__(action_id, "rotateYaw", {
            "wpml:aircraftHeading": self.aircraft_heading,
            "wpml:aircraftPathMode": self.aircraft_path_mode
        })

    @property
    def aircraft_heading(self):
        return self._aircraft_heading
    
    @aircraft_heading.setter
    def aircraft_heading(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("heading_angle must be a number.")
        if not (-180 <= value <= 180):
            raise ValueError(f"heading_angle must be in the range [-180, 180]. currently: {value}")
        self._aircraft_heading = value

    @ property
    def aircraft_path_mode(self):
        return self._aircraft_path_mode
    
    @aircraft_path_mode.setter
    def aircraft_path_mode(self, value):
        if value not in ("clockwise", "counterClockwise"):
            raise ValueError("aircraft_path_mode must be 'clockwise' or 'counterClockwise'.")
        self._aircraft_path_mode = value