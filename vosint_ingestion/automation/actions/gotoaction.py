from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class GotoAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="goto",
            display_name="Goto",
            action_type=ActionType.COMMON,
            readme="Mở địa chỉ URL",
            z_index=1,
            param_infos=[
                ParamInfo(
                    name="wait",
                    display_name="Time wait for load",
                    val_type="str",
                    default_val="0",
                    validators=["required"],
                )
            ],
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["INPUT_URL"], "msg": ["Input URL"]}
            )

        url = input_val
        # print(input_val)
        return self.driver.goto(url)
