from .model import HistoryLog
from vosint_ingestion.models import MongoRepository
from typing import *
import traceback

def addLog(action_log: Dict[str, Any]):
    try:
        id_str = MongoRepository().insert_one("action_log", action_log)
        return id_str
    except Exception as e:
        traceback.print_exc()
        raise e

def getLogs(search_params:Dict[str, Any]):
    try:
        page_size = search_params.get("page_size")
        page_index = search_params.get("page_index")
        skip = page_size*(page_index-1)
        search_filter = {"$and": []}
        if search_params.get("text_search"):
            search_filter["$and"].append(
                {
                    "$or": [
                        {"actor_name": {"$regex": search_params.get("text_search"), "$options": "i"}},
                        {"actor_role": {"$regex": search_params.get("text_search"), "$options": "i"}},
                        {"action_name": {"$regex": search_params.get("text_search"), "$options": "i"}},
                        {"target_type": {"$regex": search_params.get("text_search"), "$options": "i"}},
                        {"target_name": {"$regex": search_params.get("text_search"), "$options": "i"}},
                    ]
                }
            )
        if search_params.get("start_date"):
            search_filter["$and"].append(
                {
                    "created_at": {
                        "$gte": search_params.get("start_date")
                    }
                }
            )
        if search_params.get("end_date"):
            search_filter["$and"].append(
                {
                    "created_at": {
                        "$lte": search_params.get("end_date")
                    }
                }
            )
        if search_filter["$and"].__len__() == 0:
            search_filter = {}

        print("search_filter", search_filter)
        data = MongoRepository().get_many(
            collection_name = "action_log", 
            filter_spec = search_filter, 
            order_spec=["create_at desc"],
            pagination_spec={
                "skip": skip,
                "limit": page_size
            })
        return data
    except Exception as e:
        traceback.print_exc()
        raise e