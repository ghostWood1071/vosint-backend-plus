# from ..model import HistoryLog
from vosint_ingestion.models import MongoRepository
from typing import *
import traceback
from bson.objectid import ObjectId
import json
from core.config import settings
import requests


def add(doc_ids:List[str]):
    try:
        doc_filter = [ObjectId(id) for id in doc_ids]
        data = MongoRepository().find(
            "warehouse", 
            {
                "data:title": {
                    "$exists": True
                },
                "_id": {
                    "$in": doc_filter
                }
            },
            {
                "_id": 1,
                "id_new": "$_id",
                "url": "$data:url",
                "title": "$data:title",
                "description": "",
                "content": "$data:content",
                "label": [
                    "xxx", 
                    {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$data:class_sacthai", "1"]}, "then": "tich_cuc"},
                                {"case": {"$eq": ["$data:class_sacthai", "2"]}, "then": "tieu_cuc"}
                            ],
                            "default": "trung_tinh"
                        }
                    }
                ]
            }
        )[0]
        inserted_ids =  MongoRepository().insert_many("sentiment_dataset", data)
        return inserted_ids
    except Exception as e:
        traceback.print_exc()
        raise e

def split(train_size:float):
    try:
        random = MongoRepository().update_many(
            "sentiment_dataset",
            {}, 
            [{ "$set": { "random": { "$rand": {} } } }]
        )
        split1 = MongoRepository().update_many(
            "sentiment_dataset", 
            { "random": { "$lte": train_size } }, 
            { "$set": { "set_type": "train" } }
        )
        split2 = MongoRepository().update_many(
            "sentiment_dataset", 
            { "random": { "$gt": train_size } }, 
            { "$set": { "set_type": "test" } }
        )
        return random and split1 and split2
    except Exception as e:
        traceback.print_exc()
        raise e
    
def add_from_file(file_name:str):
    try:
        with open(file_name) as f:
            data = json.loads(f.read())
        inserted = MongoRepository().insert_many("sentiment_dataset", data)
        return inserted
    except Exception as e:
        traceback.print_exc()
        raise e
    
def train(train_params:Dict[str, Any]):
    try:
        train_api = settings.TOPIC_SENTIMENT_API + "/train"
        res = requests.post(train_api, params=json.dumps(train_api))
        if res.status_code > 200:
            raise Exception(res.text)
        return res.json()
    except Exception as e:
        traceback.print_exc()
        raise e
    
def search(text_search:str=None, set_type:str=None, page_size:int=50, page_index:int=1):
    try:
        doc_filter = {}
        if set_type:
            doc_filter["set_type"] = set_type
        if text_search:
            regex_filter = {"$regex": text_search}
            doc_filter["$or"] = [
                {"title": regex_filter},
                {"content": regex_filter},
                {"text": regex_filter}
            ]
        data = MongoRepository().get_many(
            "sentiment_dataset", 
            doc_filter, 
            ["create_at-desc"], 
            {"skip": (page_index-1)*page_size}
        )
        return data
    except Exception as e:
        traceback.print_exc()
        raise

def get_task():
    task = MongoRepository().get_one("task_logs", {"task": "sentiment"})
    return task