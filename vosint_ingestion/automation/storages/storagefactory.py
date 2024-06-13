from common.internalerror import *

from .hbasestorage import HBaseStorage


class StorageFactory:
    def __new__(cls, name: str):
        storage_cls = HBaseStorage if name == "hbase" else None
        if storage_cls is None:
            raise InternalError(
                ERROR_NOT_FOUND,
                params={"code": ["STORAGE"], "msg": [f"{name} storage"]},
            )

        return storage_cls()
