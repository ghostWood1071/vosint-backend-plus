import pymongo
from bson.objectid import ObjectId
from common.internalerror import *
from utils import get_time_now_string
from core.config import settings
from typing import *
import traceback


class MongoRepository:
    def __init__(self):
        self.__host = settings.MONGO_DETAILS
        self.__db_name = settings.DATABASE_NAME
        self.__client = None
        self.__db = None

    def __connect(self):
        self.__client = pymongo.MongoClient(host=self.__host)
        self.__db = self.__client[self.__db_name]

    def __close(self):
        if self.__client is not None and self.__db is not None:
            self.__client.close()
            self.__client = None
            self.__db = None

    def get_one(
        self, collection_name: str, filter_spec: dict = {}, filter_other: dict = {}
    ):
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not filter_spec:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["FILTER_CONDITION"], "msg": ["Filter condition"]},
            )

        # Normalize _id field
        if "_id" in filter_spec and filter_spec["_id"]:
            filter_spec["_id"] = ObjectId(filter_spec["_id"])

        doc = None
        try:
            self.__connect()
            collection = self.__db[collection_name]
            doc = collection.find_one(filter_spec, filter_other)
        finally:
            self.__close()

        return doc

    def get_many(
        self,
        collection_name: str,
        filter_spec: dict = {},
        order_spec: list[str] = [],
        pagination_spec: dict = {},
        sor_direction=-1,
        projection: dict = None,
    ) -> tuple[list, int]:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        docs = []
        total_docs = 0
        try:
            self.__connect()
            collection = self.__db[collection_name]

            # Get total documents
            total_docs = collection.count_documents(filter_spec)

            # Apply filter conditions
            query = collection.find(filter_spec, projection=projection)

            # Apply sort
            if not order_spec:
                order_spec = [("modified_at", 1)]
            else:

                def __map_order(o):
                    # Split order information to get by and direction
                    terms = o.split("-")
                    by = terms[0]
                    direction = -1 if len(terms) > 1 and terms[1] == "desc" else 1  # 1: asc; -1: desc
                    return by, direction

                order_spec = list(map(lambda o: __map_order(o), order_spec))
            query = query.sort(order_spec)

            # Apply pagination
            if pagination_spec:
                if "skip" in pagination_spec:
                    if not isinstance(pagination_spec["skip"], int):
                        raise InternalError(
                            ERROR_NOT_INTEGER,
                            params={"code": ["SKIP_VALUE"], "msg": ["Skip value"]},
                        )
                    if pagination_spec["skip"] < 0:
                        raise InternalError(
                            ERROR_NOT_LESS_THAN_0,
                            params={"code": ["SKIP_VALUE"], "msg": ["Skip value"]},
                        )
                    query = query.skip(pagination_spec["skip"])

                if "limit" in pagination_spec:
                    if not isinstance(pagination_spec["limit"], int):
                        raise InternalError(
                            ERROR_NOT_INTEGER,
                            params={"code": ["LIMIT_VALUE"], "msg": ["Limit value"]},
                        )
                    if pagination_spec["limit"] < 0:
                        raise InternalError(
                            ERROR_NOT_LESS_THAN_0,
                            params={"code": ["LIMIT_VALUE"], "msg": ["Limit value"]},
                        )
                    query = query.limit(pagination_spec["limit"])

            # Execute query
            docs = [doc for doc in query]
        finally:
            self.__close()

        return docs, total_docs

    def get_many_d(
        self,
        collection_name: str,
        filter_spec: dict = {},
        filter_other=None,
        order_spec: list[tuple] = [],
        pagination_spec: dict = {},
    ) -> tuple[list, int]:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )
        # Normalize _id field
        if "_id" in filter_spec and filter_spec["_id"]:
            filter_spec["_id"] = ObjectId(filter_spec["_id"])

        docs = []
        total_docs = 0
        try:
            self.__connect()
            collection = self.__db[collection_name]

            # Get total documents
            total_docs = collection.count_documents(filter_spec)

            # Apply filter conditions

            query = (
                collection.find(filter_spec)
                if filter_other == None
                else collection.find(filter_spec, filter_other)
            )

            # Apply sort
            if not order_spec:
                order_spec = [("modified_at", 1)]
            else:

                def __map_order(o):
                    # Split order information to get by and direction
                    terms = o.split("-")
                    by = terms[0]
                    direction = (
                        -1 if len(terms) > 1 and terms[1] == "desc" else 1
                    )  # 1: asc; -1: desc
                    return by, direction

                order_spec = list(map(lambda o: __map_order(o), order_spec))
            query = query.sort(order_spec)

            # Apply pagination
            if pagination_spec:
                if "skip" in pagination_spec:
                    if not isinstance(pagination_spec["skip"], int):
                        raise InternalError(
                            ERROR_NOT_INTEGER,
                            params={"code": ["SKIP_VALUE"], "msg": ["Skip value"]},
                        )
                    if pagination_spec["skip"] < 0:
                        raise InternalError(
                            ERROR_NOT_LESS_THAN_0,
                            params={"code": ["SKIP_VALUE"], "msg": ["Skip value"]},
                        )
                    query = query.skip(pagination_spec["skip"])

                if "limit" in pagination_spec:
                    if not isinstance(pagination_spec["limit"], int):
                        raise InternalError(
                            ERROR_NOT_INTEGER,
                            params={"code": ["LIMIT_VALUE"], "msg": ["Limit value"]},
                        )
                    if pagination_spec["limit"] < 0:
                        raise InternalError(
                            ERROR_NOT_LESS_THAN_0,
                            params={"code": ["LIMIT_VALUE"], "msg": ["Limit value"]},
                        )
                    query = query.limit(pagination_spec["limit"])

            # Execute query
            docs = [doc for doc in query]
        finally:
            self.__close()

        return docs, total_docs

    def get_many_News(
        self,
        collection_name: str,
        filter_spec: dict = {},
        order_spec: list[tuple] = [],
        pagination_spec: dict = {},
    ) -> tuple[list, int]:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        docs = []
        total_docs = 0
        try:
            self.__connect()
            collection = self.__db[collection_name]

            # Get total documents
            total_docs = collection.count_documents(filter_spec)

            # Apply filter conditions
            query = collection.find(filter_spec, {})

            # Apply sort
            if not order_spec:
                order_spec = [("modified_at", 1)]
            else:

                def __map_order(o):
                    # Split order information to get by and direction
                    terms = o.split("-")
                    by = terms[0]
                    direction = (
                        -1 if len(terms) > 1 and terms[1] == "desc" else 1
                    )  # 1: asc; -1: desc
                    return by, direction

                order_spec = list(map(lambda o: __map_order(o), order_spec))
            query = query.sort(
                [("PublishDate", -1), ("pub_date", -1), ("created_at", -1)]
            )  # (order_spec)

            # Apply pagination
            if pagination_spec:
                if "skip" in pagination_spec:
                    if not isinstance(pagination_spec["skip"], int):
                        raise InternalError(
                            ERROR_NOT_INTEGER,
                            params={"code": ["SKIP_VALUE"], "msg": ["Skip value"]},
                        )
                    if pagination_spec["skip"] < 0:
                        raise InternalError(
                            ERROR_NOT_LESS_THAN_0,
                            params={"code": ["SKIP_VALUE"], "msg": ["Skip value"]},
                        )
                    query = query.skip(pagination_spec["skip"])

                if "limit" in pagination_spec:
                    if not isinstance(pagination_spec["limit"], int):
                        raise InternalError(
                            ERROR_NOT_INTEGER,
                            params={"code": ["LIMIT_VALUE"], "msg": ["Limit value"]},
                        )
                    if pagination_spec["limit"] < 0:
                        raise InternalError(
                            ERROR_NOT_LESS_THAN_0,
                            params={"code": ["LIMIT_VALUE"], "msg": ["Limit value"]},
                        )
                    query = query.limit(pagination_spec["limit"])

            # Execute query
            docs = [doc for doc in query]
        finally:
            self.__close()

        return docs, total_docs

    def get_many_his_log(
        self,
        collection_name: str,
        filter_spec: dict = {},
        order_spec: List[tuple] = [],
        pagination_spec: dict = {},
    ) -> tuple[list, int]:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        docs = []
        total_docs = 0
        try:
            self.__connect()
            collection = self.__db[collection_name]

            # Get total documents
            total_docs = collection.count_documents(filter_spec)

            # Apply filter conditions
            query = collection.find(
                filter_spec,
                projection={"_id": 0, "pipeline_id": 0},
                skip=pagination_spec.get("skip"),
                limit=pagination_spec.get("limit"),
                sort=[("created_at", -1)],
            )
            docs = [row for row in query]
            # Apply sort
        finally:
            self.__close()

        return docs, total_docs

    def insert_one(self, collection_name: str, doc: dict) -> str:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not doc:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DOCUMENT"], "msg": ["Document"]}
            )

        if "_id" in doc:
            raise InternalError(
                ERROR_NOT_ALLOW_SPECIFY,
                params={"code": ["DOCUMENT_ID"], "msg": ["Document id"]},
            )

        doc_id = None
        try:
            self.__connect()
            collection = self.__db[collection_name]

            # Insert
            doc["created_at"] = get_time_now_string()
            doc["modified_at"] = doc["created_at"]
            insert_res = collection.insert_one(doc)
            doc_id = str(insert_res.inserted_id)
        finally:
            self.__close()

        return doc_id
    
    def insert_many(self, collection_name: str, docs: List[Dict[str, Any]]):
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not docs:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DOCUMENT"], "msg": ["Document"]}
            )
        try:
            self.__connect()
            collection = self.__db[collection_name]
            # Insert
            for doc in docs:
                doc["created_at"] = get_time_now_string()
                doc["modified_at"] = doc["created_at"]
            insert_res = collection.insert_many(docs)
            doc_ids = [str(id) for id in insert_res.inserted_ids]
        finally:
            self.__close()

        return doc_ids

    def update_one(self, collection_name: str, doc: dict) -> bool:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not doc:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DOCUMENT"], "msg": ["Document"]}
            )

        if "_id" not in doc or not doc["_id"]:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["DOCUMENT_ID"], "msg": ["Document id"]}
            )

        success = False
        try:
            self.__connect()
            collection = self.__db[collection_name]

            # Update
            doc["modified_at"] = get_time_now_string()
            filter_spec = {"_id": ObjectId(doc["_id"])}
            del doc["_id"]
            update_res = collection.update_one(filter_spec, {"$set": doc})
            success = update_res.modified_count > 0
        finally:
            self.__close()

        return success

    def update_many(
        self, collection_name: str, filter_spec: dict, action: dict
    ) -> bool:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not filter_spec:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["FILTER"], "msg": ["filter"]}
            )

        if not action:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["ACTION"], "msg": ["action"]}
            )

        success = False
        try:
            self.__connect()
            collection = self.__db[collection_name]
            # Update
            update_res = collection.update_many(filter_spec, action)
            success = update_res.modified_count > 0
        finally:
            self.__close()

        return success

    def delete_one(self, collection_name: str, filter_spec: dict) -> bool:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not filter_spec:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["FILTER_CONDITION"], "msg": ["Filter condition"]},
            )

        # Normalize _id field
        if "_id" in filter_spec and filter_spec["_id"]:
            filter_spec["_id"] = ObjectId(filter_spec["_id"])

        success = False
        try:
            self.__connect()
            collection = self.__db[collection_name]
            delete_res = collection.delete_one(filter_spec)
            if delete_res.deleted_count > 0:
                success = True
        finally:
            self.__close()

        return success

    def delete_many(self, collection_name: str, filter_spec: dict) -> int:
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )

        if not filter_spec:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["FILTER_CONDITION"], "msg": ["Filter condition"]},
            )

        try:
            self.__connect()
            result = self.__db[collection_name].delete_many(filter=filter_spec)
            return result.deleted_count
        except Exception as e:
            traceback.print_exc()
            return 0

    def aggregate(self, collection_name: str, pipeline):
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )
        data = None
        try:
            self.__connect()
            collection = self.__db[collection_name]
            cur = collection.aggregate(pipeline)
            data = [row for row in cur]

            total_docs = collection.count_documents(pipeline[0]["$match"] or {})
        finally:
            self.__close()
        return data, total_docs

    def find(
        self,
        collection_name: str,
        filter_spec: Dict[str, Any] = {},
        projection: Dict[str, Any] = None,
        pagination: Dict[str, Any] = None,
        order: List[Dict[str, Any]] = None,
    ):
        if not collection_name:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )
        try:
            self.__connect()
            collection = self.__db[collection_name]
            if projection:
                cur = collection.find(filter=filter_spec, projection=projection)
            else:
                cur = collection.find(filter=filter_spec)
            if order:
                cur.sort(order)
            if pagination:
                cur = cur.skip(pagination.get("skip")).limit(pagination.get("limit"))
            result = []
            for row in cur:
                result.append(row)
            
            total_docs = collection.count_documents(filter_spec)

        finally:
            self.__close()
        return result, total_docs
    
    def create_index(self, collection_name:str,  field_name:str, type, options:Any = None):
        if collection_name is None:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["COLLECTION_NAME"], "msg": ["Collection name"]},
            )
        if field_name is None:
            raise InternalError(
                ERROR_REQUIRED,
                params={"code": ["FIELD_NAME"], "msg": ["field name"]},
            )
        try:
            self.__connect()
            if options:
                index_result = self.__db[collection_name].create_index([(field_name, type)], **options)
            else:
                index_result = self.__db[collection_name].create_index([(field_name, type)])
            return index_result
        except Exception as e:
            traceback.print_exc()
            return None
        finally:
            self.__close()