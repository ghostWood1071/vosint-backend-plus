from vosint_ingestion.models import MongoRepository
from typing import *
from .models import Department
from bson.objectid import ObjectId
import traceback

def get_departments(text_search:str, page_size:int, page_index:int, branch_id:str)->List[Any]:
    try:
        skip = page_size*(page_index-1)
        filter_spec = {}

        if branch_id:
            filter_spec["branch_id"] = branch_id
        if text_search not in [None, ""]:
            filter_spec["$or"] = [ 
                {"department_name": {"$regex": text_search, "$options": "i"} }, 
                {"address": {"$regex": text_search, "$options": "i"}}
            ]

        aggregation_pipeline = [
            {"$match": filter_spec},
            {"$lookup": {
                "from": "branch",   
                "let": {"branch_id": {"$toObjectId": "$branch_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$branch_id"]}}}
                ],
                "as": "branch"
            }},
            {"$unwind": {"path": "$branch", "preserveNullAndEmptyArrays": True}}, 
            {"$skip": skip},  
            {"$limit": page_size},
            {
                "$project": {
                    "_id": {"$toString": "$_id"}, 
                    "department_name": 1, "phone": 1, "fax": 1, "address": 1, "active": 1, "brand_id": 1,
                    "branch_name": "$branch.branch_name",
                }
            }
        ]
        
        # result, total_docs = MongoRepository().find(**search_params)
        result, total_docs = MongoRepository().aggregate("department", aggregation_pipeline)

        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result, "total_records": total_docs }
    except Exception as e:
        traceback.print_exc()
        raise e

def get_department(department_id:str)->Any:
    try:
        result, _ = MongoRepository().find("department", filter_spec={"_id": ObjectId(department_id)})
        if len(result) == 0:
            raise Exception(f"Department {department_id} no found")

        result[0]["_id"] = str(result[0]["_id"])
        return result[0]
    except Exception as e:
        traceback.print_exc()
        raise e
    
def get_department_dropdown()->Any:
    try:
        result, _ = MongoRepository().find("department", filter_spec={})

        return [{"label": item["department_name"], "value": item["_id"]} for item in result]
    except Exception as e:
        traceback.print_exc()
        raise e

def delete_departments(department_ids:list[str])->Any:
    try:
        del_condition = [ObjectId(x) for x in department_ids]
        del_count = 0
        if len(del_condition) > 0:
            del_count = MongoRepository().delete_many("department", filter_spec={"_id": {"$in": del_condition}})
        return del_count
    except Exception as e:
        traceback.print_exc()
        raise e

def update_department(department_id:str, update_val:dict[str, Any])->Any:
    try:
        update_count = 0
        if update_val.get("department_id"):
            update_val.pop("department_id")
        update_params = {
            "collection_name": "department",
            "filter_spec": {
                "_id": ObjectId(department_id)
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

def insert_department(doc:dict[Any])->Any:
    try:
        if doc.get("department_id"):
            doc.pop("department_id")
        inserted_id = MongoRepository().insert_one("department", doc)
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise e