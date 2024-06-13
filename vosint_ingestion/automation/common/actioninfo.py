class ParamInfo:
    def __init__(
        self,
        name: str,
        display_name: str,
        val_type: str,
        default_val,
        options: list = [],
        validators: list = [],
        z_index: int = 0,
    ):
        self.name = name
        self.display_name = display_name
        self.val_type = val_type
        self.default_val = default_val
        self.options = options
        self.validators = validators
        self.z_index = z_index

    def to_json(self) -> dict:
        info = {
            "name": self.name,
            "display_name": self.display_name,
            "val_type": self.val_type,
            "default_val": self.default_val,
            "validators": self.validators,
            "z_index": self.z_index,
        }
        if self.options:
            info["options"] = self.options
        return info


class ActionInfo:
    def __init__(
        self,
        name: str,
        display_name: str,
        action_type: str,
        readme: str = "",
        param_infos: list[ParamInfo] = [],
        z_index: int = 0,
    ):
        self.name = name
        self.display_name = display_name
        self.action_type = action_type
        self.readme = readme
        self.param_infos = param_infos
        self.z_index = z_index

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "action_type": self.action_type,
            "readme": self.readme,
            "is_ctrl_flow": self.__is_ctrl_flow(self.param_infos),
            "param_infos": list(map(lambda p_info: p_info.to_json(), self.param_infos)),
            "z_index": self.z_index,
        }

    def __is_ctrl_flow(self, param_infos: list[ParamInfo]) -> bool:
        # existed = next(filter(lambda pi: pi.name == 'actions', param_infos),
        #                None)
        existed = next(filter(lambda pi: pi.name == "actions", param_infos), None)
        return existed is not None


class Multy_ParamInfo:
    def __init__(
        self,
        name: str,
        display_name: str,
        val_type: str,
        default_val,
        options: list = [],
        validators: list = [],
        z_index: int = 0,
    ):
        self.name = name
        self.display_name = display_name
        self.val_type = val_type
        self.default_val = default_val
        self.options = options
        self.validators = validators
        self.z_index = z_index

    def to_json(self) -> dict:
        info = {
            "name": self.name,
            "display_name": self.display_name,
            "val_type": self.val_type,
            "default_val": self.default_val,
            "validators": self.validators,
            "z_index": self.z_index,
        }
        if self.options:
            info["options"] = self.options
        return info