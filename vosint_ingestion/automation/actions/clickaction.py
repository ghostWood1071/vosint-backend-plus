from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class ClickAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="click",
            display_name="Click",
            action_type=ActionType.COMMON,
            readme="Click một thành phần",
            param_infos=[
                ParamInfo(
                    name="time_sleep",
                    display_name="Time_Sleep",
                    val_type="select",  # val_type='str',
                    default_val=0.3,
                    options=[i/10 for i in range(1,30)],
                    validators=["required"],
                ),
                ParamInfo(
                    name="number_click",
                    display_name="Number_Click",
                    val_type="select",  # val_type='str',
                    default_val=1,
                    options =[i for i in range(1,10)],
                    #options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11, 12, 13, 14, 15, 16, 17, 18, 19 ,20,21 ,22 ,23 ,24 ,25 ,26 ,27 ,28 ,29 ,30,31 ,32 ,33 ,34 ,35 ,36 ,37 ,38 ,39 ,40,41 ,42 ,43 ,44 ,45 ,46 ,47 ,48],
                    validators=["required"],
                ),
            ],
            z_index=7,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        from_elem = input_val
        # attr_name = self.params['attr_name']
        #print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaâ')
        for i in range(int(self.params["number_click"]) -1):
            self.driver.click(from_elem[0], time_sleep=self.params["time_sleep"])
        return self.driver.click(from_elem[0], time_sleep=self.params["time_sleep"])
