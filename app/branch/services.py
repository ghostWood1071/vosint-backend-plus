from vosint_ingestion.models import MongoRepository
from typing import *
from .models import Branch
from bson.objectid import ObjectId
import traceback

def get_branches(text_search:str, page_size:int, page_index:int)->List[Any]:
    try:
        skip = page_size*(page_index-1)
        search_params = {
            "collection_name": "branch",
            "filter_spec": {}, 
            "pagination": {
                "skip": skip,
                "limit": page_size
            },
            # "order": "sort_order",
        }


        if text_search not in [None, ""]:
            search_params.update({
                "filter_spec": {"branch_name": {"$regex": text_search, "$options": "i"}}
            })

        
        result, total_docs = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result, "total_records": total_docs }
    except Exception as e:
        traceback.print_exc()
        raise e

def get_branch(branch_id:str)->Any:
    try:
        result, _ = MongoRepository().find("branch", filter_spec={"_id": ObjectId(branch_id)})
        if len(result) == 0:
            raise Exception(f"Branch {branch_id} no found")

        result[0]["_id"] = str(result[0]["_id"])
        return result[0]
    except Exception as e:
        traceback.print_exc()
        raise e

def get_branch_dropdown()->Any:
    try:
        result, _ = MongoRepository().find("branch", filter_spec={})

        return [{"label": item["branch_name"], "value": item["_id"]} for item in result]
    except Exception as e:
        traceback.print_exc()
        raise e
    
def delete_branches(branch_ids:list[str])->Any:
    try:
        del_condition = [ObjectId(x) for x in branch_ids]
        del_count = 0
        if len(del_condition) > 0:
            del_count = MongoRepository().delete_many("branch", filter_spec={"_id": {"$in": del_condition}})
        return del_count
    except Exception as e:
        traceback.print_exc()
        raise e

def update_branch(branch_id:str, update_val:dict[str, Any])->Any:
    try:
        update_count = 0
        if update_val.get("branch_id"):
            update_val.pop("branch_id")
        update_params = {
            "collection_name": "branch",
            "filter_spec": {
                "_id": ObjectId(branch_id)
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

def insert_branch(doc:dict[Any])->Any:
    try:
        if doc.get("branch_id"):
            doc.pop("branch_id")
        inserted_id = MongoRepository().insert_one("branch", doc)
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise e