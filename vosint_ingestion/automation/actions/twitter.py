from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class TwitterAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="twitter",
            display_name="Twitter",
            action_type=ActionType.COMMON,
            readme="twitter",
            param_infos=[
                ParamInfo(
                    name="type",
                    display_name="Tài khoản lấy tin",
                    val_type="select",
                    default_val="",
                    options=['account'],
                    validators=["required_"],
                )
            ],
            z_index=15,
        )

    def exec_func(self, input_val=None, **kwargs):
        pass
