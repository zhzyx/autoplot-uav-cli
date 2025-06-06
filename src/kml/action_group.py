from .action import Action
import xmltodict

class ActionGroup:
    def __init__(self, group_id, actions=None, start_index=None, end_index=None, trigger_type='reachPoint', mode="sequence"):
        """
        Parameters:
        * group_id: Group ID (int, > 0): The ID of the action group. Normally it follows the placemark index.
        * actions: List of Action objects: The actions to be executed


        wpml:actionTriggerType: Trigger type (enum):
            - reachPoint: Executed on arrival at the waypoint.
            - betweenAdjacentPoints: Flight routine segment trigger. Rotate the gimbal evenly.
            - multipleTiming: Same time trigger.
            - multipleDistance: Same distance trigger.
        * Note: "betweenAdjacentPoints" should be used with "gimbalEvenlyRotate". 
          "multipleTiming" combined with "takePhoto" can achieve equal-time interval capture. 
          "multipleDistance" combined with "takePhoto" can achieve equal-distance interval.

        TODO: Implement the actionTriggerParam when we need to use the timeing or distance trigger.
        wpml:actionTriggerParam: Trigger parameter (float, s or m, > 0):
            - When "actionTriggerType" is "multipleTiming", this element indicates the interval time in seconds.
            - When "actionTriggerType" is "multipleDistance", this element indicates the interval distance in meters.
        """
        self.group_id = group_id
        self.start_index = start_index if start_index is not None else group_id
        self.end_index = end_index if end_index is not None else group_id
        self.mode = mode
        self.trigger_type = trigger_type
        self.actions = actions if actions else []
        
        @property
        def group_id(self):
            return self._group_id

        @group_id.setter
        def group_id(self, group_id):
            if not isinstance(group_id, int):
                raise ValueError("group_id must be an integer")
            self._group_id = group_id

        @property
        def start_index(self):
            return self._start_index

        @start_index.setter
        def start_index(self, start_index):
            if not isinstance(start_index, int):
                raise ValueError("start_index must be an integer")
            self._start_index = start_index

        @property
        def end_index(self):
            return self._end_index

        @end_index.setter
        def end_index(self, end_index):
            if not isinstance(end_index, int):
                raise ValueError("end_index must be an integer")
            self._end_index = end_index

        @property
        def mode(self):
            return self._mode

        @mode.setter
        def mode(self, mode):
            if mode not in ["sequence", "parallel"]:
                raise ValueError("mode must be 'sequence' or 'parallel'")
            self._mode = mode

        @property
        def trigger_type(self):
            return self._trigger_type

        @trigger_type.setter
        def trigger_type(self, trigger_type):
            valid_trigger_types = [
            "reachPoint",
            "betweenAdjacentPoints",
            "multipleTiming",
            "multipleDistance",
            ]
            if trigger_type not in valid_trigger_types:
                raise ValueError(
                    f"trigger_type must be one of {valid_trigger_types}"
                )
            self._trigger_type = trigger_type

        @property
        def actions(self):
            return self._actions

        @actions.setter
        def actions(self, actions):
            if not isinstance(actions, list):
                raise ValueError("actions must be a list")
            if not all(isinstance(action, Action) for action in actions):
                raise ValueError("all items in actions must be instances of Action")
            self._actions = actions

    def add_action(self, action: Action):
        if not isinstance(action, Action):
            raise ValueError("action must be an instance of Action")
        self.actions.append(action)

    def to_dict(self):
        return {
            "wpml:actionGroupId": self.group_id,
            "wpml:actionGroupStartIndex": self.start_index,
            "wpml:actionGroupEndIndex": self.end_index,
            "wpml:actionGroupMode": self.mode,
            "wpml:actionTrigger": {"wpml:actionTriggerType": self.trigger_type},
            "wpml:action": [action.to_dict() for action in self.actions]
        }

    def to_xml(self):
        data = self.to_dict()
        return xmltodict.unparse({"wpml:actionGroup": data}, pretty=True)

    @classmethod
    def from_xml(cls, xml_string):
        data = xmltodict.parse(xml_string)["wpml:actionGroup"]
        group_id = data["wpml:actionGroupId"]
        start_index = data.get("wpml:actionGroupStartIndex")
        end_index = data.get("wpml:actionGroupEndIndex")
        mode = data.get("wpml:actionGroupMode", "sequence")
        trigger_type = data["wpml:actionTrigger"]["wpml:actionTriggerType"]
        actions = [Action.from_dict(action) for action in data.get("wpml:action", [])]
        return cls(group_id, actions, start_index, end_index, trigger_type, mode)


