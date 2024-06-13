import pydantic
from bson import ObjectId, regex
from fastapi import HTTPException, status
from unidecode import unidecode
from vosint_ingestion.models.mongorepository import MongoRepository

from db.init_db import get_collection_client
import re
from datetime import datetime, timedelta
from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)

db = get_collection_client("object")
news_es = My_ElasticSearch()
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str


async def find_by_id(id: ObjectId, projection=None):
    return await db.find_one(filter={"_id": id}, projection=projection)


async def search_by_filter_and_paginate(type, skip: int, limit: int):
    query = {"type": type}
    if type:
        query["type"] = type
    offset = (skip - 1) * limit if skip > 0 else 0
    list_object = []
    async for item in db.find(query).sort("_id").skip(offset).limit(limit):
        item = object_to_json(item)
        list_object.append(item)
    return list_object


async def count_search_object(type: str):
    type_filter = {"name": type}
    return await db.count_documents(type_filter)


async def create_object(Object):
    return await db.insert_one(Object)


async def get_all_object(filter, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_object = []
    async for item in db.find(filter).sort("_id").skip(offset).limit(limit):
        item = object_to_json(item)
        list_object.append(item)
    return list_object


async def count_all_object(filter):
    return await db.count_documents(filter)


async def find_by_filter_and_paginate(
    name: str, type: str | None, skip: int, limit: int
):
    query = {"name": {"$regex": name, "$options": "i"}, "object_type": type}
    if type:
        query["object_type"] = type
    offset = (skip - 1) * limit if skip > 0 else 0
    list_object = []
    async for item in db.find(query, {"news_list": 0}).sort("_id").skip(offset).limit(
        limit
    ):
        item = object_to_json(item)
        list_object.append(item)
    return list_object


def object_to_json(Object) -> dict:
    Object["_id"] = str(Object["_id"])
    return Object


async def count_object(Type, name):
    query = {"object_type": Type, "name": {"$regex": name}}
    return await db.count_documents(query)


async def get_one_object(name: str) -> dict:
    list_object = []
    async for item in db.find(
        {
            "$or": [
                {"name": {"$regex": name}},
            ]
        }
    ):
        item = object_to_json(item)
        list_object.append(item)
    return list_object


async def update_object(id: str, data: dict):
    object = await db.find_one({"_id": ObjectId(id)})

    list_object = await db.find().to_list(length=None)

    for item in list_object:
        if item["_id"] != object["_id"] and item["name"] == data["name"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Object is duplicated"
            )

    # if object["name"] == data["name"]:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Object already exist")

    updated_object = await db.find_one_and_update({"_id": ObjectId(id)}, {"$set": data})
    if updated_object:
        return status.HTTP_200_OK
    else:
        return False


async def delete_object(id: str):
    object_deleted = await db.find_one({"_id": ObjectId(id)})
    if object_deleted:
        await db.delete_one({"_id": ObjectId(id)})
        return status.HTTP_200_OK


def get_keyword_regex(keyword_dict):
    pattern = ""
    for key in list(keyword_dict.keys()):
        pattern = pattern + keyword_dict.get(key) + ","
    keyword_arr = [keyword.strip() for keyword in pattern.split(",")]
    keyword_arr = [
        # rf"\b{keyword.strip()}\b"
        # rf"(?<!\pL\pN){re.escape(keyword.strip())}(?!\\pL\\pN)"
        # rf"(?<![\p{{L}}\p{{N}}]){re.escape(keyword.strip())}(?![\p{{L}}\p{{N}}])"
        '"' + keyword.strip() + '"'
        for keyword in list(filter(lambda x: x != "", keyword_arr))
    ]
    pattern = "|".join(keyword_arr)
    return pattern


def add_news_to_object(object_id):
    object, _ = MongoRepository().get_many("object", {"_id": ObjectId(object_id)})
    end_date = datetime.now().replace(hour=0, minute=0, second=0)
    start_date = end_date - timedelta(days=90)
    pattern = get_keyword_regex(object[0].get("keywords"))

    _start_date = datetime.strftime(start_date, "%Y-%m-%dT00:00:00Z")
    _end_date = datetime.strftime(end_date, "%Y-%m-%dT00:00:00Z")
    # search for mongo
    # filter_spec = {
    #     "$or": [
    #         # {"data:title": {"$regex": pattern, "$options": "i"}},
    #         # {"data:content": {"$regex": pattern, "$options": "i"}},
    #         {"data:title": {"$regex": pattern, "$options": "iu"}},
    #         {"data:content": {"$regex": pattern, "$options": "iu"}},
    #     ],
    #     "pub_date": {"$gte": start_date, "$lte": end_date},
    #     # "pub_date": {"$lte": end_date},
    # }

    # news, _ = MongoRepository().get_many(
    #     "News", filter_spec, ["pub_date"], {"skip": 0, "limit": 500}, sor_direction=1
    # )

    # search for elastic
    if pattern != "":
        pipeline_dtos = news_es.search_main(
            index_name="vosint",
            query=pattern,
            gte=_start_date,
            lte=_end_date,
        )

        for i in range(len(pipeline_dtos)):
            try:
                pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"]["id"]
            except:
                pass
            pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()

        news_ids = [str(_id["_id"]) for _id in pipeline_dtos]
        # print("news_ids", news_ids)
    else:
        news_ids = []

    # if len(news_ids) > 0:
    MongoRepository().update_many(
        "object",
        {"_id": {"$in": [ObjectId(object_id)]}},
        {"$set": {"news_list": news_ids}},
    )


def update_news(object_id: str):
    try:
        # object = MongoRepository().get_one("object", {"_id": object_id})
        # if object is None:
        #     return False
        # key_str = ""
        # for key in object.get("keywords").keys():
        #     key_str += object.get("keywords").get(key) + ","
        # key_arr = [key.strip() for key in key_str.split(",")]
        # key_arr = list(filter(lambda x: x != "", key_arr))
        # search_text = " | ".join(key_arr)
        # data = my_es.search_main("vosint", query=search_text, size=1000)
        # insert_list = [row.get("_id") for row in data]
        # MongoRepository().update_many(
        #     "object",
        #     {"_id": ObjectId(object_id)},
        #     {"$set": {"news_list": insert_list}},
        # )
        add_news_to_object(object_id)
        return True
    except Exception as e:
        print(e)
        return False
