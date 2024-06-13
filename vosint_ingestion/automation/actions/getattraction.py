from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction


class GetAttrAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="get_attr",
            display_name="Get Attribute",
            action_type=ActionType.COMMON,
            readme="Lấy thuộc tính của một thành phần",
            param_infos=[
                ParamInfo(
                    name="attr_name",
                    display_name="Attribute name",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                )
            ],
            z_index=5,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        from_elem = input_val
        attr_name = self.params["attr_name"]
        return self.driver.get_attr(from_elem, attr_name)
