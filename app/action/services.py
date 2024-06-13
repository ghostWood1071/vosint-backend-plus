from vosint_ingestion.models import MongoRepository
from typing import *
from .models import Action
from bson.objectid import ObjectId
import traceback

def get_actions(text_search:str, page_size:int, page_index:int, function_id:str)->List[Any]:
    try:
        skip = page_size*(page_index-1)
        search_params = {
            "collection_name": "action",
            "filter_spec": {}, 
            "pagination": {
                "skip": skip,
                "limit": page_size
            },
            # "order": "sort_order",
        }

        if text_search not in [None, ""]:
            search_params.setdefault("filter_spec", {}).update({
                "$or": [
                    {"action_name": {"$regex": text_search, "$options": "i"}},
                    {"action_code": {"$regex": text_search, "$options": "i"}},
                ]   
            })
            
        if function_id not in [None, ""]:
            search_params.setdefault("filter_spec", {}).update({"function_id": function_id})

        
        result, total_docs = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result, "total_records": total_docs }
    except Exception as e:
        traceback.print_exc()
        raise e

def get_action(action_id:str)->Any:
    try:
        result, _ = MongoRepository().find("action", filter_spec={"_id": ObjectId(action_id)})
        if len(result) == 0:
            raise Exception(f"Action {action_id} no found")

        result[0]["_id"] = str(result[0]["_id"])
        return result[0]
    except Exception as e:
        traceback.print_exc()
        raise e

def delete_actions(action_ids:list[str])->Any:
    try:
        del_condition = [ObjectId(x) for x in action_ids]
        del_count = 0
        if len(del_condition) > 0:
            del_count = MongoRepository().delete_many("action", filter_spec={"_id": {"$in": del_condition}})
        return del_count
    except Exception as e:
        traceback.print_exc()
        raise e

def update_action(action_id:str, update_val:dict[str, Any])->Any:
    try:
        update_count = 0
        if update_val.get("action_id"):
            update_val.pop("action_id")
        update_params = {
            "collection_name": "action",
            "filter_spec": {
                "_id": ObjectId(action_id)
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

def insert_action(doc:dict[Any])->Any:
    try:
        if doc.get("action_id"):
            doc.pop("action_id")
        inserted_id = MongoRepository().insert_one("action", doc)
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise e