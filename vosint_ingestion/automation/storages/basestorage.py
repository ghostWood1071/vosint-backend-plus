from abc import abstractmethod


class BaseStorage:
    @abstractmethod
    def put(self, tbl_name: str, record: dict, **params):
        raise NotImplementedError()

    @abstractmethod
    def put_bulk(self, tbl_name: str, records: list[dict], **params):
        raise NotImplementedError()
