from common.internalerror import *

from .actions import URLInputAction, get_action_class
from .common import ActionType
from .drivers import BaseDriver
from .storages import BaseStorage
from .utils import get_action_info
import asyncio
from models.mongorepository import MongoRepository

class Pipeline:
    def __init__(
        self,
        driver: BaseDriver,
        storage: BaseStorage,
        actions: list[dict],
        pipeline_id=None,
        mode_test = None,
        list_proxy = None
    ):
        if not driver:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DRIVER"], "msg": ["Driver"]}
            )

        if not storage:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["STORAGE"], "msg": ["Storage"]}
            )

        if not actions:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["ACTION_LIST"], "msg": ["List of actions"]},
            )

        # Validate the first action must be input type
        first_action = actions[0]
        if "name" not in first_action or not first_action["name"]:
            raise InternalError(
                ERROR_REQUIRED,
                params={
                    "code": ["FIRST_ACTION_NAME"],
                    "msg": ["The first action name"],
                },
            )

        first_action_info = get_action_info(first_action["name"])
        if first_action_info is None:
            raise InternalError(
                ERROR_NOT_FOUND,
                params={
                    "code": [f'{first_action["name"].upper()}_ACTION'],
                    "msg": [f'{first_action["name"]} action'],
                },
            )

        if first_action_info["action_type"] != ActionType.INPUT:
            raise InternalError(
                ERROR_NOT_INPUT,
                params={"code": ["FIRST_ACTION"], "msg": ["The first action"]},
            )

        self.__driver = driver
        self.__storage = storage
        self.__first_action = first_action
        #print(first_action)
        self.__common_actions = actions[1:]
        self.pipeline_id = pipeline_id
        self.mode_test = mode_test
        self.list_proxy = list_proxy

    def run(self):
        try:
            # Run first action
            url = self.__first_action["params"]["url"]
            id_source = self.__first_action["params"]["source"]
            action = URLInputAction(self.__driver, self.__storage, url=url)
            #print(id_nguon)
            input_val = action.run(pipeline_id=self.pipeline_id)
            #print(self.__first_action["params"]["source"])
            source_mogo = MongoRepository().get_one(collection_name='infor',filter_spec={"_id":id_source})
            
            kwargs = {
                "pipeline_id": self.pipeline_id,
                "mode_test": self.mode_test,
                "source_name": source_mogo['name'],
                "list_proxy":self.list_proxy,
                "source_host_name":source_mogo['host_name'],
                "source_language":source_mogo['language'],
                "source_publishing_country":source_mogo['publishing_country'],
                "source_source_type":source_mogo['source_type'],
                "first_action":self.__first_action
            }

            # Run from 2nd action
            for act in self.__common_actions:
                #print(act['id'])
                params = act["params"] if "params" in act else {}
                try:
                    #print(act["id"])
                    a = act["id"]
                    # print(a)
                    params["id_schema"] = a
                except:
                    pass
                #print('123',params)
                action = get_action_class(act["name"])(
                    self.__driver, self.__storage, **params
                )
                input_val = action.run(input_val, **kwargs)

            # Destroy driver after work done
        finally:
            self.__driver.destroy()

        return input_val

class Pipeline_Kafka:
    def __init__(
        self,
        driver: BaseDriver,
        storage: BaseStorage,
        actions: list[dict],
        pipeline_id=None,
        mode_test = None,
        input_val = None,
        kwargs = None
    ):
        
        if not driver:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DRIVER"], "msg": ["Driver"]}
            )

        if not storage:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["STORAGE"], "msg": ["Storage"]}
            )

        if not actions:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["ACTION_LIST"], "msg": ["List of actions"]},
            )

        # Validate the first action must be input type
        
        first_action = actions[0]
        if "name" not in first_action or not first_action["name"]:
            raise InternalError(
                ERROR_REQUIRED,
                params={
                    "code": ["FIRST_ACTION_NAME"],
                    "msg": ["The first action name"],
                },
            )
        
        first_action_info = get_action_info(first_action["name"])
        if first_action_info is None:
            raise InternalError(
                ERROR_NOT_FOUND,
                params={
                    "code": [f'{first_action["name"].upper()}_ACTION'],
                    "msg": [f'{first_action["name"]} action'],
                },
            )
        
        # if first_action_info["action_type"] != ActionType.INPUT:
        #     raise InternalError(
        #         ERROR_NOT_INPUT,
        #         params={"code": ["FIRST_ACTION"], "msg": ["The first action"]},
        #     )
       
        self.__driver = driver
        self.__storage = storage
        
        self.__common_actions = actions[0:]
        self.pipeline_id = pipeline_id
        self.mode_test = mode_test
        self.kwargs = kwargs
        self.__first_action =kwargs['first_action'] #{'name': 'url_input', 'id': 'DjqDIsluBDw03b3JKpb_Z', 'params': {'url': str(input_val), 'source': '6409502ba2c276f2ce0affe1', 'actions': []}}
        # print(kwargs['first_action'])
        # print(input_val)
        self.input_val = input_val
    def run(self):
        try:
            # Run first action
            #url = self.__first_action["params"]["url"]

            #print(url)
            action = URLInputAction(self.__driver, self.__storage, url=self.input_val)
            input_val = action.run(pipeline_id=self.pipeline_id)
            #print(self.__first_action["params"]["source"])
            kwargs = {
                "pipeline_id": self.pipeline_id,
                "mode_test": self.mode_test,
                "source_name": self.kwargs['source_name'],
                "source_host_name":self.kwargs['source_host_name'],
                "source_language":self.kwargs['source_language'],
                "source_publishing_country":self.kwargs['source_publishing_country'],
                "source_source_type":self.kwargs['source_source_type']
            }

            # Run from 2nd action
            for act in self.__common_actions:
                params = act["params"] if "params" in act else {}
                #print('123',params)
                action = get_action_class(act["name"])(
                    self.__driver, self.__storage, **params
                )
                input_val = action.run(input_val, **kwargs)

            # Destroy driver after work done
        finally:
            self.__driver.destroy()
            #pass
        return input_val