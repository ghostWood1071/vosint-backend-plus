from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class TiktokAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="tiktok",
            display_name="Tiktok",
            action_type=ActionType.COMMON,
            readme="tiktok",
            param_infos=[
                ParamInfo(
                    name="type",
                    display_name="Tài khoản lấy tin",
                    val_type="select",
                    default_val="",
                    options=['account'],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="cookies",
                    display_name="Cookies",
                    val_type="str",
                    default_val="",
                    validators=["required_"],
                )
            ],
            z_index=14,
        )

    def exec_func(self, input_val=None, **kwargs):
        pass