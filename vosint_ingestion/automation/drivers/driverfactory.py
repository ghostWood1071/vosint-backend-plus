from common.internalerror import *

from .playwrightdriver import PlaywrightDriver
from models import MongoRepository

class DriverFactory:
    def __new__(cls, name: str , id_proxy = None):
        if id_proxy != None:
            print(id_proxy)
            a = MongoRepository().get_one(collection_name="proxy",filter_spec={"_id":id_proxy})
            print(a['ip_address'])
            driver_cls = PlaywrightDriver(ip_proxy=a['ip_address'],port=a['port'],username=a['username'],password=a['password']) if name == "playwright" else None
        else:
            driver_cls = PlaywrightDriver() if name == "playwright" else None
        # driver_cls = PlaywrightDriver if name == "playwright" else None
        if driver_cls is None:
            raise InternalError(
                ERROR_NOT_FOUND, params={"code": ["DRIVER"], "msg": [f"{name} driver"]}
            )

        return driver_cls
