import happybase
from common.internalerror import *

from .basestorage import BaseStorage


class HBaseStorage(BaseStorage):
    def __init__(self):
        # TODO Move to configuration file
        self.__host = "192.168.1.30"
        self.__port = 6060
        self.__conn = None

    def __connect(self):
        if self.__conn is None:
            self.__conn = happybase.Connection(host=self.__host, port=self.__port)

    def __close(self):
        if self.__conn is not None:
            self.__conn.close()
            self.__conn = None

    def put(self, tbl_name: str, record: dict, **params):
        if not tbl_name:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["TABLE_NAME"], "msg": ["Table name"]}
            )

        if not record:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["INPUT_OBJECT"], "msg": ["Input object"]},
            )

        if "row_key" not in params or not params["row_key"]:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["ROW_KEY"], "msg": ["Row key"]}
            )

        try:
            self.__connect()
            # Create new table if not exists
            tbl_existed = next(
                filter(
                    lambda item: item.decode("utf-8") == tbl_name, self.__conn.tables()
                ),
                None,
            )
            if tbl_existed is None:
                families = {}
                for key in record.keys():
                    new_key = key.split(":")[0]
                    families[new_key] = {}
                self.__conn.create_table(tbl_name, families)

            # Put data into the table
            tbl = self.__conn.table(tbl_name)
            row = record[params["row_key"]]
            tbl.put(row, record)
        except:
            f = open("test.txt", "a")
            f.write(str(record))
            f.write("\n")
            f.close()
        finally:
            self.__close()

    def put_bulk(self, tbl_name: str, records: list[str], **params):
        if "row_key" not in params or not params["row_key"]:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["ROW_KEY"], "msg": ["Row key"]}
            )

        if not records:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["INPUT_OBJECT"], "msg": ["Input object"]},
            )

        try:
            self.__connect()
            # TODO Handle for not exists table
            tbl = self.__conn.table(tbl_name)
            # Put a batch into the table
            with tbl.batch() as batch:
                for record in records:
                    row = record[params["row_key"]]
                    batch.put(row, record)

        finally:
            self.__close()
