from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class SendKeyAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="send_key",
            display_name="Send Key",
            action_type=ActionType.COMMON,
            readme="Lấy thuộc tính của một thành phần",
            param_infos=[
                ParamInfo(
                    name="send_key",
                    display_name="Key",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                )
            ],
            z_index=9,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        from_elem = input_val
        send_key = self.params["send_key"]
        return self.driver.get_attr(from_elem, send_key)
