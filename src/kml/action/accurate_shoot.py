from .action import Action
import xmltodict

class AccurateShootAction(Action):
    # TODO: review this
    def __init__(self, action_id=0, gimbal_pitch_rotate_angle=None, gimbal_yaw_rotate_angle=None):
        super().__init__(action_id, "accurateShoot", {
            "wpml:gimbalPitchRotateAngle": gimbal_pitch_rotate_angle,
            "wpml:gimbalYawRotateAngle": gimbal_yaw_rotate_angle
        })

    @property
    def gimbal_pitch_rotate_angle(self):
        return self._action_actuator_func_param.get("wpml:gimbalPitchRotateAngle")

    @gimbal_pitch_rotate_angle.setter
    def gimbal_pitch_rotate_angle(self, value):
        if not isinstance(value, (int, float, type(None))):
            raise ValueError("gimbal_pitch_rotate_angle must be a number or None.")
        self._action_actuator_func_param["wpml:gimbalPitchRotateAngle"] = value

    @property
    def gimbal_yaw_rotate_angle(self):
        return self._action_actuator_func_param.get("wpml:gimbalYawRotateAngle")

    @gimbal_yaw_rotate_angle.setter
    def gimbal_yaw_rotate_angle(self, value):
        if not isinstance(value, (int, float, type(None))):
            raise ValueError("gimbal_yaw_rotate_angle must be a number or None.")
        self._action_actuator_func_param["wpml:gimbalYawRotateAngle"] = value

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:action"]
        params = data.get("wpml:actionActuatorFuncParam", {})
        return cls(
            action_id=data["wpml:actionId"],
            gimbal_pitch_rotate_angle=params.get("wpml:gimbalPitchRotateAngle"),
            gimbal_yaw_rotate_angle=params.get("wpml:gimbalYawRotateAngle")
        )

