from vosint_ingestion.models import MongoRepository
from typing import *
import traceback
from bson.objectid import ObjectId
from datetime import datetime

#----------------------------------------------------chung--------------------------------------------------------
def get_item(item_id:str):
   try:
        news = MongoRepository().get_one("warehouse", {"_id": ObjectId(item_id)})
        news["pub_date"] = str(news.get("pub_date"))
        return news
   except Exception as e:
       traceback.print_exc()
       raise e

def search_item(
    search_text:str, 
    end_date:str, 
    start_date:str, 
    catalog_id: str, 
    page_index: int = 1, 
    page_size: int = 50
):
    skip = (page_index-1) * page_size
    filter = {}
    if catalog_id:
        filter["catalog_id"] = catalog_id
    if search_text and catalog_id:
        filter["$or"] = [
            {"file_path": {"$regex": search_text}},
            {"file_name": {"$regex": search_text}},
            {"data:title": {"$regex": search_text}},
            {"data:content": {"$regex": search_text}}
        ]  
    filter["$and"] = []
    if start_date:
        filter["$and"].append({"created_at": {"$gte": start_date}})
    if end_date:
        filter["$and"].append({"created_at": {"$lte": end_date}})
    if len(filter["$and"]) == 0:
        filter.pop("$and")
    try:
        print(filter)
        data = MongoRepository().get_many_News(
            "warehouse", 
            filter, 
            pagination_spec={
                "skip": skip,
                "limit": page_size
            }
        )
        return data
    except Exception as e:
        traceback.print_exc()
        raise e 

def statistic():
    aggs = [
        {
            '$match': {
                'catalog_id': None
            }
        }, 
        {
            '$count': 'count'
        }
    ]
    try:
        catalogs = MongoRepository().get_many(
            "catalog", 
            {},  
            projection={"_id": 1, "catalog_name": 1}
        )[0]
        
        for catalog in catalogs:
            if catalog.get("_id") is not None:
                catalog["_id"] = str(catalog["_id"])
            aggs[0]["$match"]["catalog_id"] = catalog.get("_id")
            count_result = MongoRepository().aggregate("warehouse", aggs)[0]
            if len(count_result) > 0:
                catalog["count"] = count_result[0].get("count")
            else:
                catalog["count"] = 0
        return catalogs
    except Exception as e:
        traceback.print_exc()
        raise e

#----------------------------------------------------news----------------------------------------------------------

def add_news(news_ids:List[str], catalog_id:str) :
    try:
        object_ids = [ObjectId(id) for id in news_ids]
        data = MongoRepository().find(**{
            "collection_name": "News",
            "filter_spec": {"_id": {"$in": object_ids}}
        })[0]
        for row in data:
            row["catalog_id"] = catalog_id
        inserted_ids = MongoRepository().insert_many("warehouse", data)
        if len(inserted_ids) == 0:
            raise Exception("insert error")
        return inserted_ids
    except Exception as e:
        traceback.print_exc()
        raise e

def add_doc(doc:Dict[str, Any]):
    try:
        name_map = {
            "data_class_chude": "data:class_chude",
            "data_class_linhvuc": "data:class_linhvuc",
            "data_title": "data:title",
            "data_content": "data:content",
            "data_url": "data:url",
            "data_author": "data:author",
            "data_time": "data:time",
            "data_html": "data:html",
            "data_title_translate": "data:title_translate",
            "data_content_translate": "data:content_translate",
            "data_class_sacthai": "data:class_sacthai"
        }
        tmp_doc = doc.copy()
        for key in doc.keys():
            if not name_map.get(key):
                continue
            tmp_doc[name_map[key]] = tmp_doc[key]
            tmp_doc.pop(key)
        tmp_doc["pub_date"] = datetime.now()
        del doc
        inserted = MongoRepository().insert_one("warehouse", tmp_doc)
        return inserted
    except Exception as e:
        traceback.print_exc()
        raise e

def delete_news(news_ids:List[str]) :
    try:
        object_ids = [ObjectId(id) for id in news_ids]
        deleted_count = MongoRepository().delete_many(
            collection_name = "warehouse",
            filter_spec = {"_id": {"$in": object_ids}}
        )
        return deleted_count
    except Exception as e:
        traceback.print_exc()
        raise e

#-------------------------------------------file----------------------------------------------------------    

def add_file(file_path:str, catalog_id:str, file_name:str):
    try:
        inserted = MongoRepository().insert_one("warehouse", {
            "file_path": file_path,
            "catalog_id": catalog_id,
            "file_name": file_name
        })
        return inserted
    except Exception as e:
        traceback.print_exc()
        raise e
    
def delete_file(file_id: str):
    try:
        deleted = MongoRepository().delete_one("warehouse", {"_id": ObjectId(file_id)})
        return deleted
    except Exception as e:
        traceback.print_exc()
        raise e
    
