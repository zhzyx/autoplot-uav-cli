import xmltodict

class Action:
    """
    Action specific parameters stored in action_actuator_func_param(actionActuatorFuncParam).
    """
    def __init__(self, action_id=0, actuator_func=None, action_actuator_func_param=None):
        self._action_id = action_id
        self._actuator_func = actuator_func
        self._action_actuator_func_param = action_actuator_func_param or {}

    @property
    def action_id(self):
        return self._action_id

    @action_id.setter
    def action_id(self, value):
        if not isinstance(value, int):
            raise ValueError("action_id must be an integer.")
        self._action_id = value

    @property
    def actuator_func(self):
        return self._actuator_func

    @actuator_func.setter
    def actuator_func(self, value):
        if not isinstance(value, str):
            raise ValueError("actuator_func must be a string.")
        self._actuator_func = value

    @property
    def action_actuator_func_param(self):
        return self._action_actuator_func_param

    @action_actuator_func_param.setter
    def action_actuator_func_param(self, value):
        if not isinstance(value, dict):
            raise ValueError("action_actuator_func_param must be a dictionary.")
        self._action_actuator_func_param = value

    def set_action_actuator_func_param(self, key, value):
        if not isinstance(key, str):
            raise ValueError("key must be a string.")
        if not isinstance(value, (str, int, float)):
            raise ValueError("value must be a string, integer, or float.")
        self._action_actuator_func_param[key] = value

    def get_action_actuator_func_param(self, key):
        if not isinstance(key, str):
            raise ValueError("key must be a string.")
        return self._action_actuator_func_param.get(key)

    def update_param(self, key, value):
        self._action_actuator_func_param[f"wpml:{key}"] = value

    def to_dict(self):
        return {
            "wpml:actionId": self._action_id,
            "wpml:actionActuatorFunc": self._actuator_func,
            **({"wpml:actionActuatorFuncParam": self._action_actuator_func_param} if self._action_actuator_func_param else {})
        }

    def to_xml(self):
        return xmltodict.unparse({"wpml:action": self.to_dict()}, pretty=True)

    @classmethod
    def from_xml(cls, xml_data):
        data = xmltodict.parse(xml_data)["wpml:action"]
        return cls(
            action_id=data["wpml:actionId"],
            actuator_func=data.get("wpml:actionActuatorFunc"),
            action_actuator_func_param=data.get("wpml:actionActuatorFuncParam", {})
        )





    


    

 

