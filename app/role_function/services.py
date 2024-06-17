from vosint_ingestion.models import MongoRepository
from typing import *
from .models import InsertRoleFunction
from bson.objectid import ObjectId
import traceback
from db.init_db import get_collection_client

def get_function_by_role_id(role_id)->List[Any]:
    try:
        search_params = {
            "collection_name": "role_function",
            "filter_spec": {"role_id": role_id}, 
        }

        result, _ = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result }
    except Exception as e:
        traceback.print_exc()
        raise e

async def insert_role_function(doc: dict) -> Any:
    try:
        role_function_client = get_collection_client("role_function")
        function_client = get_collection_client("function")
        
        all_function_ids = []
        async for func in function_client.find({}, {"_id": 1}):
            all_function_ids.append(str(func['_id']))

        role_id = doc.get("role_id")    
        # function_ids = doc.get("function_ids")
        function_ids = list(set(doc.get("function_ids") + all_function_ids))

        count = await role_function_client.count_documents({"role_id": role_id})
        documents = [{"role_id": role_id, "function_id": function_id} for function_id in function_ids]


        if(len(documents) == 0):
            filter_spec = {"role_id": role_id}
            del_count = MongoRepository().delete_many("role_function", filter_spec=filter_spec)
            return "deleted"
        else: 
            if(len(documents) < count):
                filter_spec={"role_id": role_id, "function_id": {"$nin": function_ids}}
                del_count = MongoRepository().delete_many("role_function", filter_spec=filter_spec)
                return "deleted"
            else:

                distinct_function_ids = await role_function_client.distinct("function_id", {"role_id": role_id})
                function_ids = list(set(function_ids) - set(distinct_function_ids))
                print("ids", function_ids)
                record = [{"role_id": role_id, "function_id": function_id} for function_id in function_ids]
                print("record", record)
                inserted_ids = await role_function_client.insert_many(record)

        # del_count = MongoRepository().delete_many("role_function", filter_spec={"role_id": role_id})
        return "inserted_ids"

    except Exception as e:
        traceback.print_exc()
        raise e