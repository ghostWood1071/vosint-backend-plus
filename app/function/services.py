from vosint_ingestion.models import MongoRepository
from typing import *
from .models import Function
from bson.objectid import ObjectId
import traceback
from db.init_db import get_collection_client

def get_functions(text_search:str, page_size:int, page_index:int, plus: bool = False)->List[Any]:
    try:
        collection_target = "function_plus" if plus else "function"
        skip = page_size*(page_index-1)
        search_params = {
            "collection_name": collection_target,
            "filter_spec": {}, 
            "pagination": {
                "skip": skip,
                "limit": page_size
            },
            "order": "sort_order",
        }

        if text_search not in [None, ""]:
            search_params.setdefault("filter_spec", {}).update({
                "$or": [
                    {"function_name": {"$regex": text_search, "$options": "i"}},
                    {"url": {"$regex": text_search, "$options": "i"}},
                ]   
            })
            
        result, total_docs = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result, "total_records": total_docs }
    except Exception as e:
        traceback.print_exc()
        raise e

def get_function(function_id:str, plus: bool = False)->Any:
    try:
        collection_target = "function_plus" if plus else "function"
        
        result, _ = MongoRepository().find(collection_target, filter_spec={"_id": ObjectId(function_id)})
        if len(result) == 0:
            raise Exception(f"Function {function_id} no found")

        result[0]["_id"] = str(result[0]["_id"])
        return result[0]
    except Exception as e:
        traceback.print_exc()
        raise e

def delete_functions(function_ids:list[str], plus: bool = False)->Any:
    try:
        collection_target = "function_plus" if plus else "function"

        del_condition = [ObjectId(x) for x in function_ids]
        del_count = 0
        if len(del_condition) > 0:
            del_count = MongoRepository().delete_many(collection_target, filter_spec={"_id": {"$in": del_condition}})
        return del_count
    except Exception as e:
        traceback.print_exc()
        raise e

def update_function(function_id:str, update_val:dict[str, Any], plus: bool = False)->Any:
    try:
        collection_target = "function_plus" if plus else "function"

        update_count = 0
        if update_val.get("function_id"):
            update_val.pop("function_id")
        update_params = {
            "collection_name": collection_target,
            "filter_spec": {
                "_id": ObjectId(function_id)
            },
            "action": {
                "$set": update_val
            }
        }

        # update max child: 3 
        update_params_child = {
            "collection_name": collection_target,
            "filter_spec": {
                "parent_id": str(function_id)
            },
            "action": {
                "$set": {"level": update_val["level"] + 1}
            }
        }
        update_count = MongoRepository().update_many(**update_params)
        updated_child = MongoRepository().update_many(**update_params_child)

        updated_child_res, _ = MongoRepository().find(collection_target, filter_spec={"parent_id": str(function_id)})

        if(len(updated_child_res) > 0):
            update_params_child_2 = {
                "collection_name": collection_target,
                "filter_spec": {
                    "parent_id": str(updated_child_res[0]["_id"])
                },
                "action": {
                    "$set": {"level": updated_child_res[0]["level"] + 1}
                }
            }
            updated_child_2 = MongoRepository().update_many(**update_params_child_2)

        return update_count
    except Exception as e:
        traceback.print_exc()
        raise e

def insert_function(doc:dict[Any], plus: bool = False)->Any:
    try:
        collection_target = "function_plus" if plus else "function"

        if doc.get("function_id"):
            doc.pop("function_id")
        inserted_id = MongoRepository().insert_one(collection_target, doc)
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise e

async def get_active_functions(role_id: str, plus: bool = False)->List[Any]:
    try:
        collection_target = "function_plus" if plus else "function"

        result, _ = MongoRepository().find("role_function", filter_spec={"role_id": role_id})
        function_ids = [ObjectId(record["function_id"]) for record in result]

        search_params = {
            "collection_name": collection_target,
            "filter_spec": {"_id": { "$in" : function_ids }}, 
            "order": "sort_order",
        }

        result, total_docs = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result, "total_records": total_docs }
    
    except Exception as e:
        traceback.print_exc()
        raise e