from .action import Action
import xmltodict

class FocusAction(Action):
    """
    FocusAction Parameters:
    - wpml:payloadPositionIndex (int): The position where the payload is mounted.
        Refer to the gimbalindex field in type-subtype-gimbalindex in Enumeration Values of Camera in the Product Support page.
    - wpml:isPointFocus (bool): Whether to focus on a point.
        Options: 0 (Area Focusing), 1 (Point Focusing).
    - wpml:focusX (float): Focal position on the X-axis.
        Range: [0, 1]. 0 is the leftmost, 1 is the rightmost.
    - wpml:focusY (float): Focal position on the Y-axis.
        Range: [0, 1]. 0 is the topmost, 1 is the bottommost.
    - wpml:focusRegionWidth (float): Focusing region width ratio.
        Range: [0, 1]. Required if "isPointFocus" is 0 (area focus).
    - wpml:focusRegionHeight (float): Focusing region height ratio.
        Range: [0, 1]. Required if "isPointFocus" is 0 (area focus).
    - wpml:isInfiniteFocus (bool): Whether to use infinite focus.
        Options: 0 (Not infinite focus), 1 (Infinite focus).
    """
    def __init__(self, action_id=0, payload_position_index=0, is_point_focus=False, focus_x=0.4, focus_y=0.4, focus_region_width=0.2, focus_region_height=0.2, is_infinite_focus=False):
        super().__init__(action_id, "focus", {
            "wpml:payloadPositionIndex": payload_position_index,
            "wpml:isPointFocus": 1 if is_point_focus else 0,
            "wpml:focusX": focus_x,
            "wpml:focusY": focus_y,
            "wpml:focusRegionWidth": focus_region_width,
            "wpml:focusRegionHeight": focus_region_height,
            "wpml:isInfiniteFocus": 1 if is_infinite_focus else 0
        })

    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:action"]
        params = data.get("wpml:actionActuatorFuncParam", {})
        return cls(
            action_id=data["wpml:actionId"],
            payload_position_index=params.get("wpml:payloadPositionIndex"),
            is_point_focus=bool(params.get("wpml:isPointFocus", 0)),
            focus_x=params.get("wpml:focusX"),
            focus_y=params.get("wpml:focusY"),
            focus_region_width=params.get("wpml:focusRegionWidth"),
            focus_region_height=params.get("wpml:focusRegionHeight"),
            is_infinite_focus=bool(params.get("wpml:isInfiniteFocus", 0))
        )