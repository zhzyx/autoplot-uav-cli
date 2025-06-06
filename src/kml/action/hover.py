from .action import Action
import xmltodict

class HoverAction(Action):
    def __init__(self, action_id=0, hover_time=None):
        '''
        Note:
        - hover_time is in seconds and should be between 1 and 30. The dji pilot 2 app seems round the float to int
        '''
        super().__init__(action_id, "hover", {
            "wpml:hoverTime": hover_time
        })

    @property
    def hover_time(self):
        return self._action_actuator_func_param.get("wpml:hoverTime")

    @hover_time.setter
    def hover_time(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("hover_time must be a number.")
        if value < 1 or value > 30:
            raise ValueError("Dji hover_time only support between 1 and 30 seconds.")
        self._action_actuator_func_param["wpml:hoverTime"] = value

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:action"]
        params = data.get("wpml:actionActuatorFuncParam", {})
        return cls(
            action_id=data["wpml:actionId"],
            hover_time=params.get("wpml:hoverTime")
        )