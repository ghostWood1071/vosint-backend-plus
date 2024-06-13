from vosint_ingestion.models import MongoRepository
from typing import *
from .models import Role
from bson.objectid import ObjectId
import traceback

def get_roles(text_search:str, page_size:int, page_index:int)->List[Any]:
    try:
        skip = page_size*(page_index-1)
        search_params = {
            "collection_name": "role",
            "filter_spec": {}, 
            "pagination": {
                "skip": skip,
                "limit": page_size
            },
            # "order": "sort_order",
        }


        if text_search not in [None, ""]:
            search_params.update({
                "filter_spec": {"role_name": {"$regex": text_search, "$options": "i"}}
            })

        result, total_docs = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result, "total_records": total_docs }
    except Exception as e:
        traceback.print_exc()
        raise e

def get_role(role_id:str)->Any:
    try:
        result, _ = MongoRepository().find("role", filter_spec={"_id": ObjectId(role_id)})
        if len(result) == 0:
            raise Exception(f"Role {role_id} no found")

        result[0]["_id"] = str(result[0]["_id"])
        return result[0]
    except Exception as e:
        traceback.print_exc()
        raise e

def get_role_dropdown()->Any:
    try:
        result, _ = MongoRepository().find("role", filter_spec={})

        return [{"label": item["role_name"], "value": item["_id"]} for item in result]
    except Exception as e:
        traceback.print_exc()
        raise e
    
def delete_roles(role_ids:list[str])->Any:
    try:
        del_condition = [ObjectId(x) for x in role_ids]
        del_count = 0
        if len(del_condition) > 0:
            del_count = MongoRepository().delete_many("role", filter_spec={"_id": {"$in": del_condition}})
        return del_count
    except Exception as e:
        traceback.print_exc()
        raise e

def update_role(role_id:str, update_val:dict[str, Any])->Any:
    try:
        update_count = 0
        if update_val.get("role_id"):
            update_val.pop("role_id")
        update_params = {
            "collection_name": "role",
            "filter_spec": {
                "_id": ObjectId(role_id)
            },
            "action": {
                "$set": update_val
            }
        }
        update_count = MongoRepository().update_many(**update_params)
        return update_count
    except Exception as e:
        traceback.print_exc()
        raise e

def insert_role(doc:dict[Any])->Any:
    try:
        if doc.get("role_id"):
            doc.pop("role_id")
        inserted_id = MongoRepository().insert_one("role", doc)
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise e