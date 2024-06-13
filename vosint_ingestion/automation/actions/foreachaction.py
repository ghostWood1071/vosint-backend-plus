from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo
from .baseaction import BaseAction

from models.kafka_producer import KafkaProducer_class
from .clickaction import ClickAction
from .getattraction import GetAttrAction
from .getnewsinfoaction import GetNewsInfoAction
from .geturlsaction import GetUrlsAction
from .gotoaction import GotoAction
from .login import LoginAction
from .selectaction import SelectAction
from .foraction import ForAction
from .scrollaction import ScrollAction
from .hoveraction import HoverAction
from .facebook import FacebookAction


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
        else ForeachAction
        if name == "foreach"
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
        else FacebookAction
        if name == "fb"
        else None
    )
    if action_cls is None:
        raise InternalError(
            ERROR_NOT_FOUND,
            params={"code": [f"{name.upper()}_ACTION"], "msg": [f"{name} action"]},
        )

    return action_cls


class ForeachAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="foreach",
            display_name="Foreach",
            action_type=ActionType.COMMON,
            readme="Cấu trúc lặp cho mỗi phần tử",
            param_infos=[
                ParamInfo(
                    name="actions",
                    display_name="List of actions",
                    val_type="list",
                    default_val=[],
                    validators=["required"],
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
            z_index=6,
        )

    def exec_func(self, input_val=None, **kwargs):
        actions = self.params["actions"]
        flatten = False if "flatten" not in self.params else self.params["flatten"]
        # print(input_val)
        # Run foreach actions
        res = []
        if input_val is not None:
            for val in input_val:
                # print("val",val)
                # print("kwargs",kwargs)
                # print("actions",actions)

                message = {"actions": actions, "input_val": val, "kwargs": kwargs}
                # message1 = {'name': 'John', 'age': 30, 'city': 'New hkahsdjk'}
                if str(self.params["send_queue"]) == "True":
                    # print('write to kafka ...')
                    # print(message)
                    KafkaProducer_class().write("crawling_", message)
                    # print('write to kafka ...')
                    if (
                        kwargs["mode_test"] == True
                    ):  # self.params['test_pipeline'] == 'True':
                        # print(val)
                        break
                else:
                    if flatten == False:
                        res.append(self.__run_actions(actions, val, **kwargs))
                    else:
                        res += self.__run_actions(actions, val, **kwargs)
                    if (
                        kwargs["mode_test"] == True
                    ):  # self.params['test_pipeline'] == 'True':
                        # print(val)
                        break
        return res

    def __run_actions(self, actions: list[dict], input_val, **kwargs):
        tmp_val = input_val
        for act in actions:
            params = act["params"] if "params" in act else {}
            try:
                # print(act["id"])
                a = act["id"]
                # print(a)
                params["id_schema"] = a
            except:
                pass
            action = get_action_class(act["name"])(self.driver, self.storage, **params)
            tmp_val = action.run(tmp_val, **kwargs)
        return tmp_val
