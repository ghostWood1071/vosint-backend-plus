from vosint_ingestion.models import MongoRepository
from typing import *
import traceback
from bson.objectid import ObjectId
from datetime import datetime
from datetime import datetime, timedelta

def get_source_from_source_group(
    group_id:str=None,
    order_by:List[str]=[],
    page_index:int=1,
    page_size:int=50
):
    try:
        sort_by = {
            "$sort": {k:-1 for k in order_by}
        }

        pipelines = [
            {
                '$match': {
                    '_id': ObjectId(group_id)
                }
            }, 
            {
                '$unwind': '$news'
            }, 
            {
                '$project': {
                    'source_name': 1, 
                    'news_id': {
                        '$toObjectId': '$news.id'
                    }
                }
            }, 
            {
                '$lookup': {
                    'from': 'info', 
                    'localField': 'news_id', 
                    'foreignField': '_id', 
                    'as': 'info'
                }
            }, 
            {
                '$unwind': '$info'
            },
            {
                '$project': {
                    '_id': '$info._id', 
                    'source_name': 1, 
                    'name': '$info.name', 
                    'host_name': '$info.host_name', 
                    'priority': {'$ifNull': ['$info.priority', 0]}, 
                    'crawl_times': {
                        '$ifNull': [
                            '$info.crawl_times', []
                        ]
                    }
                }
            },
            {
                '$addFields': {
                    'count_times': {
                        '$size': '$crawl_times'
                    }
                }
            }
        ]
        
        
        if sort_by.get("$sort").get("priority"):
            sort_by["$sort"]["priority"] = 1

        if len(order_by) > 0:
            pipelines.append(sort_by)

        pipelines.append(
            {
                "$facet": {
                    "data": [
                        {"$skip": (page_index-1)*page_size},
                        {"$limit": page_size}
                    ],
                    "count": [
                        {"$count": "value"}
                    ]
                }
            }
        )    
        data = MongoRepository().aggregate("Source", pipelines)[0][0]
        result = [data.get("data"), data.get("count")[0].get("value")]
        return result
    except Exception as e:
        traceback.print_exc()
        raise e
    
def statisitic_source_by_time(source_host_name:str):
    try:
        now = datetime.now()
        start_date = now - timedelta(days=1000)
        pipeline = [
            {
                '$match': {
                    'source_host_name': source_host_name
                }
            }, 
            {
                '$addFields': {
                    'created_at': {
                        '$dateFromString': {
                            'dateString': '$created_at'
                        }
                    }
                }
            },  
            {
                '$addFields': {
                    'create_hour': {
                        '$hour': '$created_at'
                    }
                }
            },
            {
                "$match": {
                    "created_at": {'$gte': start_date, '$lte': now}
                }
            },
            {
                '$group': {
                    '_id': '$create_hour', 
                    'count': {
                        '$sum': 1
                    }
                }
            }
        ]
        agg_result = {val.get("_id"):val.get("count") for val in MongoRepository().aggregate("News", pipeline)[0]}
        result = {x: agg_result.get(x) if agg_result.get(x) is not None else 0 for x in range(0, 25)}
        print(pipeline)
        return result
    except Exception as e:
        traceback.print_exc()
        raise e

def save_suggest_crawl_times(source_id:str, crawl_times:List[str]=[]):
    try:
        updated = MongoRepository().update_many(
            "info", 
            {"_id": ObjectId(source_id)}, 
            {"$set": {"crawl_times":crawl_times}}
        )
        return updated
    except Exception as e:
        traceback.print_exc()
        raise e
    