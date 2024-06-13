import time
from abc import abstractmethod
from fastapi import status
from common.internalerror import *
from models import HBaseRepository, MongoRepository

from ..common import ActionInfo, ActionStatus
from ..drivers import BaseDriver
from ..storages import BaseStorage


class BaseAction:
    def __init__(self, driver: BaseDriver, storage: BaseStorage, **params):
        self.set_status(ActionStatus.INITIALIZING)

        # Validate input driver
        if not driver:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DRIVER"], "msg": ["Driver"]}
            )

        # Validate storage
        if not storage:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["STORAGE"], "msg": ["Storage"]}
            )

        # Validate input parameters
        self.__validate_params(**params)

        self.driver = driver
        self.storage = storage
        self.params = params
        #print(params)
        

        self.set_status(ActionStatus.INITIALIZED)

    def __validate_params(self, **params):
        action_info = self.get_action_info()
        # print('aaaaaaaaaaaaaaaaaa',action_info.param_infos)
        for p_info in action_info.param_infos:
            # print("p_info",p_info.validators)
            validators = p_info.validators
            # Validate with validators
            if validators:
                for v in validators:
                    if v == "required":
                        # print('p_info.name',p_info.name)
                        # print('params',str(params))
                        # print(p_info.name not in params)
                        # print('abc',not '')
                        if p_info.name not in params or not params[p_info.name]:
                            raise InternalError(
                                ERROR_REQUIRED,
                                params={
                                    "code": [p_info.display_name.upper()],
                                    "msg": [p_info.display_name],
                                },
                            )
            
            # Validate value must be in options
            # print('params',str(params))
            # print('1p_info.options', p_info.options)
            # print('1.5',p_info.name)
            # print('2params[p_info.name]',params[p_info.name])
            # print('3???',params[p_info.name] not in p_info.options)
            if (p_info.default_val==None or p_info.default_val==[]) and (p_info.options and params[p_info.name] not in p_info.options):
                # print('1p_info.options', p_info.options)
                # print('2params[p_info.name]',params[p_info.name])
                # print('3???',params[p_info.name] not in p_info.options)
                #print('aaaaaaaaaaaaaaaaaaaaaaaaa')
                options = ", ".join(list(map(lambda o: str(o), p_info.options)))
                raise InternalError(
                    ERROR_NOT_IN,
                    params={
                        "code": [p_info.display_name.upper()],
                        "msg": [p_info.display_name, f"[{options}]"],
                    },
                )

    @classmethod
    @abstractmethod
    def get_action_info(cls) -> ActionInfo:
        raise NotImplementedError()

    def run(self, input_val=None, **kwargs):
        tmp_val = ""
        res =""
        self.set_status(ActionStatus.RUNNING)
        #print(kwargs)
        
        try:
            res = self.exec_func(input_val, **kwargs)
            history = self.return_str_status(ActionStatus.COMPLETED)
            his_log = {}
            his_log["pipeline_id"] = kwargs["pipeline_id"]
            his_log["actione"] = f"{self.__class__.__name__}"
            his_log["log"] = history
            his_log["link"] = "" if type(input_val) != str else input_val
            #his_log["id_schema"] = self.params['id_schema']
            his_log['message_error'] = ''
        except Exception as e:
            history = self.return_str_status(ActionStatus.ERROR)
            his_log = {}
            his_log["pipeline_id"] = kwargs["pipeline_id"]
            his_log["actione"] = f"{self.__class__.__name__}"
            his_log["log"] = history
            his_log["link"] = "" if type(input_val) != str else input_val
            #print('abbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',his_log["actione"])
            his_log["id_schema"] = self.params['id_schema']
            his_log['message_error'] = str(e).replace('=========================== logs ===========================','').replace('============================================================','')

            MongoRepository().insert_one(collection_name="his_log", doc=his_log)
            res = self.exec_func(input_val, **kwargs)
            

        

        # Wait if necessary
        if "wait" in self.params and self.params["wait"]:
            wait_secs = float(self.params["wait"])
            print(f"Waiting {wait_secs}s...")
            time.sleep(wait_secs)

        return res

    @abstractmethod
    def exec_func(self, input_val=None, **kwargs):
        raise NotImplementedError()

    def get_status(self) -> str:
        return self.__status

    def set_status(self, status: str):
        self.__status = status
        print(f"{self.__class__.__name__} ==> {self.__status}")
        # return f'{self.__class__.__name__} ==> {self.__status}'

    def return_str_status(self, status: str):
        return status
    
