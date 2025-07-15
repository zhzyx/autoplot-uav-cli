from .action import Action
import xmltodict

class GimbalRotateAction(Action):
    """
    GimbalRotateAction Parameters:
    - wpml:payloadPositionIndex (int): The position where the payload is mounted.
        Refer to the gimbalindex field in type-subtype-gimbalindex in Enumeration Values of Camera in the Product Support page.
    - wpml:gimbalHeadingYawBase (enum): Gimbal yaw angle rotation coordinate system.
        Options: "north" (Relative geographic north). 
        Note: The offical documentation gives only this option. But seems it not working and related to drone north
    - wpml:gimbalRotateMode (enum): Gimbal rotation mode.
        Options: "absoluteAngle" (The angle relative to the North). 
        Note: The offical documentation gives only this option.
    - wpml:gimbalPitchRotateEnable (bool): Whether to enable pitch rotation of the gimbal.
        Options: 0 (disable), 1 (enable).
    - wpml:gimbalPitchRotateAngle (float): Pitch rotation angle.
        Note: Different gimbals can be turned in different ranges.
    - wpml:gimbalRollRotateEnable (bool): Whether to enable roll rotation of the gimbal.
        Options: 0 (disable), 1 (enable).
    - wpml:gimbalRollRotateAngle (float): Roll rotation angle.
        Note: Different gimbals can be turned in different ranges.
    - wpml:gimbalYawRotateEnable (bool): Whether to enable yaw rotation of the gimbal.
        Options: 0 (disable), 1 (enable).
    - wpml:gimbalYawRotateAngle (float): Yaw rotation angle.
        Note: Different gimbals can be turned in different ranges.
    - wpml:gimbalRotateTimeEnable (bool): Whether to turn on the gimbal rotation time.
        Options: 0 (disable), 1 (enable).
    - wpml:gimbalRotateTime (float): Time to complete rotation of the gimbal (in seconds).
    """
    def __init__(
        self,
        action_id=0,
        payload_position_index=0,
        gimbal_pitch_rotate_enable=False,
        gimbal_pitch_rotate_angle=None,
        gimbal_roll_rotate_enable=False,
        gimbal_roll_rotate_angle=None,
        gimbal_yaw_rotate_enable=False,
        gimbal_yaw_rotate_angle=None,
        gimbal_rotate_time_enable=False,
        gimbal_rotate_time=0,
        gimbal_heading_yaw_base="north",
        gimbal_rotate_mode="absoluteAngle"
    ):
        if gimbal_heading_yaw_base not in ("north",):
            raise ValueError("gimbal_heading_yaw_base must be 'north'.")
        if gimbal_rotate_mode not in ("absoluteAngle",):
            raise ValueError("gimbal_rotate_mode must be 'absoluteAngle'.")
        if gimbal_pitch_rotate_enable and gimbal_pitch_rotate_angle is None:
            raise ValueError("gimbal_pitch_rotate_angle cannot be None when gimbal_pitch_rotate_enable is True.")
        if gimbal_roll_rotate_enable and gimbal_roll_rotate_angle is None:
            raise ValueError("gimbal_roll_rotate_angle cannot be None when gimbal_roll_rotate_enable is True.")
        if gimbal_yaw_rotate_enable and gimbal_yaw_rotate_angle is None:
            raise ValueError("gimbal_yaw_rotate_angle cannot be None when gimbal_yaw_rotate_enable is True.")

        super().__init__(action_id, "gimbalRotate", {
            "wpml:payloadPositionIndex": payload_position_index,
            "wpml:gimbalHeadingYawBase": gimbal_heading_yaw_base,
            "wpml:gimbalRotateMode": gimbal_rotate_mode,
            "wpml:gimbalPitchRotateEnable": 1 if gimbal_pitch_rotate_enable else 0,
            "wpml:gimbalPitchRotateAngle": gimbal_pitch_rotate_angle if gimbal_pitch_rotate_enable else None,
            "wpml:gimbalRollRotateEnable": 1 if gimbal_roll_rotate_enable else 0,
            "wpml:gimbalRollRotateAngle": gimbal_roll_rotate_angle if gimbal_roll_rotate_enable else None,
            "wpml:gimbalYawRotateEnable": 1 if gimbal_yaw_rotate_enable else 0,
            "wpml:gimbalYawRotateAngle": gimbal_yaw_rotate_angle if gimbal_yaw_rotate_enable else None,
            "wpml:gimbalRotateTimeEnable": 1 if gimbal_rotate_time_enable else 0,
            "wpml:gimbalRotateTime": gimbal_rotate_time if gimbal_rotate_time_enable else None
        })

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:action"]
        params = data.get("wpml:actionActuatorFuncParam", {})
        return cls(
            action_id=data["wpml:actionId"],
            payload_position_index=params.get("wpml:payloadPositionIndex"),
            gimbal_heading_yaw_base=params.get("wpml:gimbalHeadingYawBase", "north"),
            gimbal_rotate_mode=params.get("wpml:gimbalRotateMode", "absoluteAngle"),
            gimbal_pitch_rotate_enable=bool(params.get("wpml:gimbalPitchRotateEnable", 0)),
            gimbal_pitch_rotate_angle=params.get("wpml:gimbalPitchRotateAngle"),
            gimbal_roll_rotate_enable=bool(params.get("wpml:gimbalRollRotateEnable", 0)),
            gimbal_roll_rotate_angle=params.get("wpml:gimbalRollRotateAngle"),
            gimbal_yaw_rotate_enable=bool(params.get("wpml:gimbalYawRotateEnable", 0)),
            gimbal_yaw_rotate_angle=params.get("wpml:gimbalYawRotateAngle"),
            gimbal_rotate_time_enable=bool(params.get("wpml:gimbalRotateTimeEnable", 0)),
            gimbal_rotate_time=params.get("wpml:gimbalRotateTime")
        )