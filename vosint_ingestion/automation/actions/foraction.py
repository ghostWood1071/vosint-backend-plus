from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction
# from .foreachaction import get_action_class
from .clickaction import ClickAction
from .getattraction import GetAttrAction
from .getnewsinfoaction import GetNewsInfoAction
from .geturlsaction import GetUrlsAction
from .gotoaction import GotoAction
from .login import LoginAction
from .selectaction import SelectAction
# from .foraction import ForAction
from .scrollaction import ScrollAction
from .hoveraction import HoverAction

def get_action_class(name: str):
    action_cls = (
        GotoAction
        if name == "goto"
        else GetUrlsAction
        if name == "get_urls"
        else GetNewsInfoAction
        if name == "get_news_info"
        else SelectAction
        if name == "select"
        else GetAttrAction
        if name == "get_attr"
        # else ForeachAction
        # if name == "foreach"
        else ClickAction
        if name == "click"
        else ForAction
        if name == "for"
        else LoginAction
        if name == "login"
        else ScrollAction
        if name == "scroll"
        else HoverAction
        if name == "hover"
        else None
    )
    if action_cls is None:
        raise InternalError(
            ERROR_NOT_FOUND,
            params={"code": [f"{name.upper()}_ACTION"], "msg": [f"{name} action"]},
        )

    return action_cls

class ForAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="for",
            display_name="For",
            action_type=ActionType.COMMON,
            readme="For ...",
            param_infos=[
                ParamInfo(
                    name="actions",
                    display_name="List of actions",
                    val_type="list",
                    default_val=[],
                    validators=["required"],
                ),
                ParamInfo(
                    name="start",
                    display_name="Start",
                    val_type="select",  # val_type='str',
                    default_val=1,
                    options=[i for i in range(0,10)],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="end",
                    display_name="End",
                    val_type="select",  # val_type='str',
                    default_val=1,
                    options=[i for i in range(1,100)],
                    validators=["required"],
                ),
                ParamInfo(
                    name="run_first",
                    display_name="Run_First",
                    val_type="select",  # val_type='str',
                    default_val="True",
                    options=["True","False"],
                    validators=["required"],
                ),
            ],
            z_index=12,
        )

    def exec_func(self, input_val=None, **kwargs):
        actions = self.params["actions"]
        flatten = False if "flatten" not in self.params else self.params["flatten"]

        res = []
        for i in range(self.params['start'],self.params['end']):
            #print(i)
            if str(self.params['run_first']) == 'False':
                if i == self.params['start']:
                    continue
            flatten = True
            if input_val is not None:
                val = input_val
                if flatten == False:
                    res.append(self.__run_actions(actions, val, **kwargs))
                else:
                    #print('????????????????????????????????????????????????????????????????????????????????')
                    res += self.__run_actions(actions, val, **kwargs)
                if kwargs["mode_test"]==True:#self.params['test_pipeline'] == 'True':
                    #print(val)
                    break
        return set(res)

    def __run_actions(self, actions: list[dict], input_val, **kwargs):
        tmp_val = input_val
        for act in actions:
            params = act["params"] if "params" in act else {}
            action = get_action_class(act["name"])(self.driver, self.storage, **params)
            tmp_val = action.run(tmp_val, **kwargs)
        return tmp_val
