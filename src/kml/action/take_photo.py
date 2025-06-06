from .action import Action
import xmltodict

class TakePhotoAction(Action):
    """
    Parameters for the take photo action:
    - fileSuffix (string): This suffix is appended to the name of the generated media file.
    - useGlobalPayloadLensIndex (bool): Whether to use the global storage type.
      0: Do not use the global set.
      1: Use the global set.
    - payloadPositionIndex (int): The position where the payload is mounted.
      Refer to the gimbalindex field in type-subtype-gimbalindex in Enumeration Values of Camera in the Product Support page.
    TODO: payloadLensIndex; not used in M300.
    """
    def __init__(self, action_id=0, file_suffix=None, use_global_payload_lens_index=0, payload_position_index=0):
        super().__init__(action_id, "takePhoto", {
            "wpml:payloadPositionIndex": payload_position_index,
            "wpml:fileSuffix": file_suffix,
            "wpml:useGlobalPayloadLensIndex": use_global_payload_lens_index
        })

    @property
    def file_suffix(self):
        return self._action_actuator_func_param.get("wpml:fileSuffix")

    @file_suffix.setter
    def file_suffix(self, value):
        if not isinstance(value, (str, type(None))):
            raise ValueError("file_suffix must be a string or None.")
        # TODO: check string, only letters, digits and dash("-") alloweed
        self._action_actuator_func_param["wpml:fileSuffix"] = value

    @property
    def use_global_payload_lens_index(self):
        return self._action_actuator_func_param.get("wpml:useGlobalPayloadLensIndex")

    @use_global_payload_lens_index.setter
    def use_global_payload_lens_index(self, value):
        if value not in (0, 1):
            raise ValueError("use_global_payload_lens_index must be 0 or 1.")
        self._action_actuator_func_param["wpml:useGlobalPayloadLensIndex"] = value

    @property
    def payload_position_index(self):
        return self._action_actuator_func_param.get("wpml:payloadPositionIndex")

    @payload_position_index.setter
    def payload_position_index(self, value):
        if not isinstance(value, int):
            raise ValueError("payload_position_index must be an integer.")
        self._action_actuator_func_param["wpml:payloadPositionIndex"] = value

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:action"]
        params = data.get("wpml:actionActuatorFuncParam", {})
        return cls(
            action_id=data["wpml:actionId"],
            file_suffix=params.get("wpml:fileSuffix"),
            use_global_payload_lens_index=int(params.get("wpml:useGlobalPayloadLensIndex", 0)),
            payload_position_index=int(params.get("wpml:payloadPositionIndex", 0))
        )

