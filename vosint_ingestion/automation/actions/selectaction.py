from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo, SelectorBy
from .baseaction import BaseAction


class SelectAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="select",
            display_name="Select",
            action_type=ActionType.COMMON,
            readme="Lấy danh sách các thành phần từ thành phần gốc",
            param_infos=[
                ParamInfo(
                    name="by",
                    display_name="Select by",
                    val_type="select",  # val_type='str',
                    default_val=SelectorBy.CSS,
                    options=SelectorBy.to_list(),
                    validators=["required"],
                ),
                ParamInfo(
                    name="expr",
                    display_name="Expression",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
            ],
            z_index=2,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        from_elem = input_val
        by = self.params["by"]
        expr = self.params["expr"]
        return self.driver.select(from_elem, by, expr)
