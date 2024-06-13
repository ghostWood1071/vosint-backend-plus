from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class TTXVNAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="ttxvn",
            display_name="TTXVN",
            action_type=ActionType.COMMON,
            readme="Thông tấn xã Việt Nam",
            param_infos=[
                ParamInfo(
                    name="limit",
                    display_name="Limit",
                    val_type="select",
                    default_val=20,
                    options=[i * 20 for i in range(1, 10)],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="is_root",
                    display_name="is_root",
                    val_type="bool",
                    default_val="True",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="send_queue",
                    display_name="Send_Queue",
                    val_type="select",
                    default_val="True",
                    options=["False", "True"],
                    validators=["required_"],
                ),
            ],
            z_index=20,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        from_elem = input_val
        ttxvn = self.params["ttxvn"]
        return self.driver.get_attr(from_elem, ttxvn)
