from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo, SelectorBy
from .baseaction import BaseAction


class LoginAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="login",
            display_name="Login",
            action_type=ActionType.COMMON,
            readme="Login",
            param_infos=[
                ParamInfo(
                    name="cookies",
                    display_name="save cookies",
                    val_type="select",  # val_type='str',
                    default_val="False",
                    options=["True", "False"],
                    validators=["required"],
                ),
                ParamInfo(
                    name="by",
                    display_name="Select by",
                    val_type="select",  # val_type='str',
                    default_val=SelectorBy.CSS,
                    options=SelectorBy.to_list(),
                    validators=["required"],
                ),
                ParamInfo(
                    name="user_expr",
                    display_name="User Expression",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
                ParamInfo(
                    name="user_key",
                    display_name="User Key",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
                ParamInfo(
                    name="password_expr",
                    display_name="Password Expression",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
                ParamInfo(
                    name="password_key",
                    display_name="Password Key",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
                ParamInfo(
                    name="login_expr",
                    display_name="Login Expression",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
            ],
            z_index=10,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
            )

        url = input_val
        by = self.params["by"]
        user_expr = self.params["user_expr"]
        user_key = self.params["user_key"]
        password_expr = self.params["password_expr"]
        password_key = self.params["password_key"]
        login_expr = self.params["login_expr"]

        page = self.driver.goto(url)
        elems = self.driver.select(page, by, user_expr)
        self.driver.sendkey(elems[0], user_key)
        elems = self.driver.select(page, by, password_expr)
        self.driver.sendkey(elems[0], password_key)
        elems = self.driver.select(page, by, login_expr)

        return self.driver.click(elems[0])
