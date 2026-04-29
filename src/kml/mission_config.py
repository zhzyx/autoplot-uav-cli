"""
DJI's missionConfig.
"""

import xmltodict

class PayloadInfo:
    def __init__(self, payload_id, payload_type, payload_sub_type, payload_name):
        self.payload_id = payload_id
        self.payload_type = payload_type
        self.payload_sub_type = payload_sub_type
        self.payload_name = payload_name

    @property
    def payload_id(self):
        return self._payload_id

    @payload_id.setter
    def payload_id(self, value):
        if not isinstance(value, int):
            raise ValueError("payload_id must be an integer.")
        self._payload_id = value

    @property
    def payload_type(self):
        return self._payload_type

    @payload_type.setter
    def payload_type(self, value):
        if not isinstance(value, int):
            raise ValueError("payload_type must be an integer.")
        self._payload_type = value

    @property
    def payload_sub_type(self):
        return self._payload_sub_type

    @payload_sub_type.setter
    def payload_sub_type(self, value):
        if not isinstance(value, int):
            raise ValueError("payload_sub_type must be an integer.")
        self._payload_sub_type = value

    @property
    def payload_name(self):
        return self._payload_name

    @payload_name.setter
    def payload_name(self, value):
        if not isinstance(value, str):
            raise ValueError("payload_name must be a string.")
        self._payload_name = value

    def to_dict(self):
        return {
            "wpml:payloadEnumValue": self.payload_id,
            "wpml:payloadSubEnumValue": self.payload_sub_type,
            "wpml:payloadPositionIndex": 0,
            "wpml:customPayloadName": self.payload_name
        }

    def to_xml(self):
        return xmltodict.unparse({"wpml:payloadInfo": self.to_dict()}, pretty=True)

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:payloadInfo"]
        return cls(
            payload_id=int(data["wpml:payloadEnumValue"]),
            payload_type=0,  # Assuming payload_type is not in XML
            payload_sub_type=int(data["wpml:payloadSubEnumValue"]),
            payload_name=data["wpml:customPayloadName"]
        )


def create_P1_payload_info():
    """
    Create a Zenmuse P1 PayloadInfo object with default values.
    """
    return PayloadInfo(50, 0, 0, "P1")

def create_AQ600_PRO_payload_info():
    """
    Create a AQ600 PRO PayloadInfo object with default values.
    TODO: add extra parameters (sensor, customPayloadActionInfo etc) for AQ600 PRO
    """
    return PayloadInfo(65534, 0, 0, "AQ600 PRO")


class DroneInfo:
    def __init__(self, drone_id, drone_sub_id):
        self.drone_id = drone_id
        self.drone_sub_id = drone_sub_id

    @property
    def drone_id(self):
        return self._drone_id

    @drone_id.setter
    def drone_id(self, value):
        if not isinstance(value, int):
            raise ValueError("drone_id must be an integer.")
        self._drone_id = value

    @property
    def drone_sub_id(self):
        return self._drone_sub_id

    @drone_sub_id.setter
    def drone_sub_id(self, value):
        if not isinstance(value, int):
            raise ValueError("drone_sub_id must be an integer.")
        self._drone_sub_id = value

    def to_dict(self):
        return {
            "wpml:droneEnumValue": self.drone_id,
            "wpml:droneSubEnumValue": self.drone_sub_id
        }

    def to_xml(self):
        return xmltodict.unparse({"wpml:droneInfo": self.to_dict()}, pretty=True)

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:droneInfo"]
        return cls(
            drone_id=int(data["wpml:droneEnumValue"]),
            drone_sub_id=int(data["wpml:droneSubEnumValue"])
        )

def create_M300_drone_info():
    """
    Create a M300 DroneInfo object with default values.
    """
    return DroneInfo(60, 0)

def create_M350_drone_info():
    """
    Create a M350 DroneInfo object with default values.
    """
    return DroneInfo(89, 0)

def create_M400_drone_info():
    """
    Create a M400 DroneInfo object with default values.
    """
    return DroneInfo(103, 0)

class MissionConfig:
    def __init__(self, fly_to_wayline_mode="safely", finish_action="goHome", exit_on_rc_lost="executeLostAction",
                 execute_rc_lost_action="goBack", take_off_security_height=5, take_off_ref_point=None,
                 global_transitional_speed=5, payload_info=None, drone_info=None):
        self.fly_to_wayline_mode = fly_to_wayline_mode
        self.finish_action = finish_action
        self.exit_on_rc_lost = exit_on_rc_lost
        self.execute_rc_lost_action = execute_rc_lost_action
        self.take_off_security_height = take_off_security_height
        self.take_off_ref_point = take_off_ref_point or [0.0, 0.0, 0.0]
        self.global_transitional_speed = global_transitional_speed
        self.payload_info = payload_info or PayloadInfo(50, 0, 0, "P1")
        self.drone_info = drone_info or create_M300_drone_info()

    @property
    def fly_to_wayline_mode(self):
        return self._fly_to_wayline_mode

    @fly_to_wayline_mode.setter
    def fly_to_wayline_mode(self, value):
        if value not in ["safely", "pointToPoint"]:
            raise ValueError("fly_to_wayline_mode must be 'safely' or 'pointToPoint'.")
        self._fly_to_wayline_mode = value

    @property
    def finish_action(self):
        return self._finish_action

    @finish_action.setter
    def finish_action(self, value):
        if value not in ["goHome", "gotoFirstWaypoint", "autoLand", "noAction"]:
            raise ValueError("finish_action must be 'goHome', 'gotoFirstWaypoint', or 'autoLand'.")
        self._finish_action = value

    @property
    def exit_on_rc_lost(self):
        return self._exit_on_rc_lost

    @exit_on_rc_lost.setter
    def exit_on_rc_lost(self, value):
        if value not in ["executeLostAction", "goContinue"]:
            raise ValueError("exit_on_rc_lost must be 'executeLostAction' or 'goContinue'.")
        self._exit_on_rc_lost = value

    @property
    def execute_rc_lost_action(self):
        return self._execute_rc_lost_action

    @execute_rc_lost_action.setter
    def execute_rc_lost_action(self, value):
        if value not in ["goBack", "landing", "hover"]:
            raise ValueError("execute_rc_lost_action must be 'goBack', 'landing', or 'hover'.")
        self._execute_rc_lost_action = value

    @property
    def take_off_security_height(self):
        return self._take_off_security_height

    @take_off_security_height.setter
    def take_off_security_height(self, value):
        if not (1.2 <= value <= 1500):
            raise ValueError("take_off_security_height must be between 1.2 and 1500.")
        self._take_off_security_height = value

    @property
    def take_off_ref_point(self):
        return self._take_off_ref_point

    @take_off_ref_point.setter
    def take_off_ref_point(self, value):
        if not (isinstance(value, list) and len(value) == 3):
            raise ValueError("take_off_ref_point must be a list of [latitude, longitude, altitude].")
        self._take_off_ref_point = value

    @property
    def global_transitional_speed(self):
        return self._global_transitional_speed

    @global_transitional_speed.setter
    def global_transitional_speed(self, value):
        if value <= 0:
            raise ValueError("global_transitional_speed must be greater than 0.")
        self._global_transitional_speed = value

    @property
    def payload_info(self):
        return self._payload_info

    @payload_info.setter
    def payload_info(self, value):
        if not isinstance(value, PayloadInfo):
            raise ValueError("payload_info must be an instance of PayloadInfo.")
        self._payload_info = value

    def to_dict(self):
        return {
            "wpml:flyToWaylineMode": self.fly_to_wayline_mode,
            "wpml:finishAction": self.finish_action,
            "wpml:exitOnRCLost": self.exit_on_rc_lost,
            "wpml:executeRCLostAction": self.execute_rc_lost_action,
            "wpml:takeOffSecurityHeight": self.take_off_security_height,
            "wpml:takeOffRefPoint": f"{self.take_off_ref_point[0]},{self.take_off_ref_point[1]},{self.take_off_ref_point[2]}",
            "wpml:globalTransitionalSpeed": self.global_transitional_speed,
            "wpml:payloadInfo": self.payload_info.to_dict(),
            "wpml:droneInfo": self.drone_info.to_dict() 
        }

    def to_xml(self):
        return xmltodict.unparse({"wpml:missionConfig": self.to_dict()}, pretty=True)

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:missionConfig"]
        payload_info = PayloadInfo.from_xml(xmltodict.unparse({"wpml:payloadInfo": data["wpml:payloadInfo"]}))
        return cls(
            fly_to_wayline_mode=data["wpml:flyToWaylineMode"],
            finish_action=data["wpml:finishAction"],
            exit_on_rc_lost=data["wpml:exitOnRCLost"],
            execute_rc_lost_action=data["wpml:executeRCLostAction"],
            take_off_security_height=float(data["wpml:takeOffSecurityHeight"]),
            take_off_ref_point=[float(x) for x in data["wpml:takeOffRefPoint"].split(",")],
            global_transitional_speed=float(data["wpml:globalTransitionalSpeed"]),
            payload_info=payload_info
        )


