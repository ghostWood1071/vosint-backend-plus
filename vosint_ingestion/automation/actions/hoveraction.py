from common.internalerror import *

from ..common import ActionInfo, ActionType
from .baseaction import BaseAction


class HoverAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="hover",
            display_name="Hover",
            action_type=ActionType.COMMON,
            readme="Hover",
            z_index=11,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["INPUT_URL"], "msg": ["Input URL"]}
            )

        return self.driver.hover(input_val)