from .drivers import DriverFactory
from .pipeline import Pipeline
from .storages import StorageFactory


class Session:
    def __init__(
        self, driver_name: str, storage_name: str, actions: list[dict], pipeline_id=None,mode_test =None
    ):
        #print('proxy',str(actions[0]['params']['proxy_list'][0]))
        if str(actions[0]['params']['proxy_list']) == '[]' or str(actions[0]['params']['proxy_list']) == '[None]':
            self.__driver = DriverFactory(driver_name)
        else:
            self.__driver = DriverFactory(name = driver_name,id_proxy = actions[0]['params']['proxy_list'][0])
        self.__storage = StorageFactory(storage_name)
        self.__pipeline = Pipeline(self.__driver, self.__storage, actions, pipeline_id ,mode_test,list_proxy = actions[0]['params']['proxy_list'])
        #print(actions)

    def start(self):
        print("Started session!")
        res = self.__pipeline.run()
        print("Finished session!")

        return res
