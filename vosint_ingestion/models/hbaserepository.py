import happybase
from common.internalerror import *


class HBaseRepository:
    def __init__(self):
        # TODO Move to configuration file
        self.__host = "192.168.1.8"
        self.__port = 6060
        self.__conn = None

    def __connect(self):
        if self.__conn is None:
            self.__conn = happybase.Connection(host=self.__host, port=self.__port)

    def __close(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None

    # def get_many(self, tbl_name: str) -> tuple[list, int]:
    #     if not tbl_name:
    #         raise InternalError(
    #             ERROR_REQUIRED, params={"code": ["TABLE_NAME"], "msg": ["Table name"]}
    #         )

    #     docs = []
    #     total_docs = 0
    #     try:
    #         self.__connect()
    #         tbl = self.__conn.table(bytes(tbl_name, "utf-8"))

    #         rows = tbl.scan()
    #         for key, row in rows:
    #             docs.append(row[b"data:content"])
    #         total_docs = len(docs)
    #     finally:
    #         self.__close()

    #     return docs, total_docs
