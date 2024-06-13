from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class ScrollAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="scroll",
            display_name="Scroll",
            action_type=ActionType.COMMON,
            readme="Cuộn trang web",
            param_infos=[
                ParamInfo(
                    name="number_scroll",
                    display_name="Scroll page number",
                    val_type="select",
                    default_val=1,
                    #options = [1,2,3,4,5],
                    options=[i for i in range(1,10)],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="time_sleep",
                    display_name="Time_Sleep",
                    val_type="select",  # val_type='str',
                    default_val=0.3,
                    #options = [0.1,0.3,0.5,1],
                    options=[i/10 for i in range(1,20)],
                    validators=["required_"],
                ),
            ],
            z_index=8,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        from_elem = input_val
        number_scroll = int(self.params["number_scroll"])
        return self.driver.scroll(from_elem, number_scroll, time_sleep=self.params["time_sleep"])
