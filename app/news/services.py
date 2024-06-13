# import datetime
from datetime import datetime
import json
from typing import *
from bson.objectid import ObjectId

from db.init_db import get_collection_client

from .utils import news_to_json
from vosint_ingestion.models import MongoRepository
from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)
from vosint_ingestion.features.job.services.get_news_from_elastic import (
    get_news_from_cart,
    build_search_query_by_keyword
)

from elasticsearch import helpers

client = get_collection_client("News")
events_client = get_collection_client("events")
news_es = My_ElasticSearch()


async def find_news_by_filter(filter, projection=None):
    news = []
    async for new in client.find(filter, projection).sort("_id"):
        new = news_to_json(new)
        news.append(new)

    return news


async def find_news_by_filter_and_paginate(
    filter_news, projection, skip: int, limit: int
):
    offset = (skip - 1) * limit if skip > 0 else 0
    news = []
    async for new in client.find(filter_news, projection).sort("_id").skip(
        offset
    ).limit(limit):
        new = news_to_json(new)
        if "is_read" not in new:
            await client.aggregate([{"$addFields": {"is_read": False}}]).to_list(
                length=None
            )

        if "list_user_read" not in new:
            await client.aggregate([{"$addFields": {"list_user_read": []}}]).to_list(
                length=None
            )

        if "event_list" not in new:
            await client.aggregate([{"$addFields": {"event_list": []}}]).to_list(
                length=None
            )
        news.append(new)
    return news


async def count_news(filter_news):
    return await client.count_documents(filter_news)


async def find_news_by_id(news_id: ObjectId):
    # projection["pub_date"] = str(projection["pub_date"])
    # return await client.find_one({"_id": news_id}, projection)
    return await client.find_one({"_id": news_id})


async def read_by_id(news_ids: List[str], user_id: str):
    news_id_list = [ObjectId(news_id) for news_id in news_ids]
    return await client.update_many(
        {"_id": {"$in": news_id_list}, "list_user_read": {"$not": {"$all": [user_id]}}},
        {"$set": {"is_read": True}, "$push": {"list_user_read": user_id}},
    )


async def unread_news(new_ids: List[str], user_id: str):
    news_id_list = [ObjectId(row_new) for row_new in new_ids]
    news_filter = {"_id": {"$in": news_id_list}}
    return await client.update_many(
        news_filter, {"$pull": {"list_user_read": {"$in": [user_id]}}}
    )


async def find_news_by_ids(ids: List[str], projection: Dict["str", Any]):
    list_ids = []
    for index in ids:
        list_ids.append(ObjectId(index))
    news_list = []
    async for news in client.find({"_id": {"$in": list_ids}}, projection):
        news_list.append(news)
    return news_list


def add_keywords_to_elasticsearch(index, keywords, doc_ids):
    es = My_ElasticSearch()
    actions = []
    for document_id in doc_ids:
        update_action = {
            "_op_type": "update",
            "_index": index,
            "_id": document_id,
            "script": {
                "source": """
                if (ctx._source.{keywords} == null) {{
                    ctx._source.{keywords} = [];
                }}
                ctx._source.{keywords}.addAll(params.values_to_add);
            """,
                "params": {"values_to_add": keywords},
            },
        }
    actions.append(update_action)
    ressult = helpers.bulk(es.es, actions)
    print(ressult)


def get_check_news_contain_list(news_ids, keywords):
    object_filter = [ObjectId(object_id) for object_id in news_ids]
    news, _ = MongoRepository().get_many("News", {"_id": {"$in": object_filter}})
    for item in news:
        item["is_contain"] = False
        item["_id"] = str(item["_id"])
        item["pub_date"] = str(item["pub_date"])
        for keyword in keywords:
            if (
                keyword.lower() in item["data:title"].lower()
                or keyword.lower() in item["data:content"].lower()
                or keyword.lower() in item["keywords"]
            ):
                item["is_contain"] = True
                break
    return news


def check_news_contain_keywords(
    object_ids: List[str], news_ids: List[str], new_keywords: List[str] = []
):
    object_filter = [ObjectId(object_id) for object_id in object_ids]
    objects, _ = MongoRepository().get_many("object", {"_id": {"$in": object_filter}})
    keywords = []
    for object in objects:
        if object.get("keywords"):
            for keyword in list(object["keywords"].values()):
                item_key_words = [key.strip() for key in keyword.split(",")]
                keywords.extend(item_key_words)
    if len(new_keywords) > 0:
        keywords.extend(new_keywords)
    while "" in keywords:
        keywords.remove("")
    print(keywords)
    result = get_check_news_contain_list(news_ids, keywords)
    return result


def remove_news_from_object(news_ids: List[str], object_ids: List[str]):
    object_filter = {"_id": {"$in": [ObjectId(object_id) for object_id in object_ids]}}
    news_id_values = [news_id for news_id in news_ids]
    object_filter["news_list"] = {"$all": news_id_values}
    result = MongoRepository().update_many(
        "object", object_filter, {"$pull": {"news_list": {"$in": news_id_values}}}
    )
    return result


def add_news_to_object(object_ids: List[str], news_ids: List[str]):
    object_filter = {"_id": {"$in": [ObjectId(object_id) for object_id in object_ids]}}
    news_id_values = [news_id for news_id in news_ids]
    object_filter["news_list"] = {"$not": {"$all": news_id_values}}
    result = MongoRepository().update_many(
        "object", object_filter, {"$push": {"news_list": {"$each": news_id_values}}}
    )
    return result


def get_timeline(
    text_search="",
    page_number=None,
    page_size=None,
    start_date: str = "",
    end_date: str = "",
    sac_thai: str = "",
    language_source: str = "",
    object_id: str = "",
):
    filter_spec = {}
    skip = int(page_size) * (int(page_number) - 1)
    if text_search != "" and object_id == "":
        filter_spec.update({"$text": {"$search": text_search.strip()}})

    if end_date != None and end_date != "":
        _end_date = datetime.strptime(end_date, "%d/%m/%Y")
        filter_spec.update({"date_created": {"$lte": _end_date}})
    if start_date != None and start_date != "":
        _start_date = datetime.strptime(start_date, "%d/%m/%Y")

        if filter_spec.get("date_created") == None:
            filter_spec.update({"date_created": {"$gte": _start_date}})
        else:
            filter_spec["date_created"].update({"$gte": _start_date})
    if sac_thai != None and sac_thai != "":
        filter_spec.update({"data:class_sacthai": sac_thai})
    if language_source != None and language_source != "":
        filter_spec.update({"source_language": language_source})

    data = []

    if object_id != "":
        filter_search = {}
        if text_search != "":
            filter_search.update({"$text": {"$search": text_search.strip()}})

        query = [
            {"$match": filter_search},
            # {"$addFields": {"score": {"$meta": "textScore"}}},
            {
                "$facet": {
                    "data": [
                        {"$match": filter_spec},
                        {"$unwind": "$new_list"},
                        {
                            "$lookup": {
                                "from": "object",
                                "let": {"news_id": "$new_list"},
                                "pipeline": [
                                    {
                                        "$match": {
                                            "news_list": {"$ne": None},
                                            "$expr": {
                                                "$in": ["$$news_id", "$news_list"]
                                            },
                                        }
                                    }
                                ],
                                "as": "result",
                            }
                        },
                        {
                            "$match": {
                                "result": {"$ne": []},
                                "result._id": ObjectId(object_id),
                            },
                        },
                        {"$project": {"result": 0}},
                        {"$skip": skip},
                        {
                            "$limit": int(page_size),
                        },
                        {"$sort": {"date_created": -1}},
                    ],
                    "total": [
                        {"$match": filter_spec},
                        {"$unwind": "$new_list"},
                        {
                            "$lookup": {
                                "from": "object",
                                "let": {"news_id": "$new_list"},
                                "pipeline": [
                                    {
                                        "$match": {
                                            "news_list": {"$ne": None},
                                            "$expr": {
                                                "$in": ["$$news_id", "$news_list"]
                                            },
                                        }
                                    }
                                ],
                                "as": "result",
                            }
                        },
                        {
                            "$match": {
                                "result": {"$ne": []},
                                "result._id": ObjectId(object_id),
                            },
                        },
                        {"$project": {"result": 0}},
                        {"$count": "count"},
                    ],
                }
            },
        ]

        # if len(filter_spec.keys()) > 2:
        #     print(1)
        # query.insert(0, {"$match": filter_spec})

        data, _ = MongoRepository().aggregate("events", query)
        total_records = data[0]["total"][0]["count"] if data[0]["total"] else 0
        data = data[0]["data"] if data[0]["data"] else []

    else:
        data, total_records = MongoRepository().get_many(
            "events",
            filter_spec,
            ["date_created"],
            {"skip": int(page_size) * (int(page_number) - 1), "limit": int(page_size)},
        )

    for row in data:
        row["_id"] = str(row["_id"])
        row["date_created"] = str(row.get("date_created"))
        if row.get("new_list") != None and type(row.get("new_list")) == str:
            row["new_list"] = [row["new_list"]]
    return {"data": data, "total_records": total_records}


async def statistics_sentiments(filter_spec, params):
    news_letter_id = params.get("newsletter_id")
    query = ""
    if news_letter_id != "" and news_letter_id != None:
        news_letter = MongoRepository().get_one(
            collection_name="newsletter", filter_spec={"_id": news_letter_id}
        )
        # nếu không là giỏ tin
        if news_letter_id != "" and news_letter["tag"] != "gio_tin":
            #lay tin theo tu khoa trich tu van ban mau
            query = build_search_query_by_keyword(news_letter)
            if params.get("text_search") not in [None, ""]:
                query = f'({query}) +("{params.get("text_search")}")'
    
    if query == "":
        query = params.get("text_search")

    if news_letter_id != "" and news_letter_id != None:
    #if params["text_search"] != None and params["text_search"] != "":
        total_docs = news_es.count_search_main(
            index_name="vosint",
            query=query,
            gte=params["start_date"],
            lte=params["end_date"],
            lang=params["language_source"],
            sentiment=params["sentiment"],
        )

        total_positive = news_es.count_search_main(
            index_name="vosint",
            query=query,
            gte=params["start_date"],
            lte=params["end_date"],
            lang=params["language_source"],
            sentiment="1"
            if params["sentiment"] == "" or params["sentiment"] == "1"
            else 9999,
        )

        total_negative = news_es.count_search_main(
            index_name="vosint",
            query=query,
            gte=params["start_date"],
            lte=params["end_date"],
            lang=params["language_source"],
            sentiment="2"
            if params["sentiment"] == "" or params["sentiment"] == "2"
            else 9999,
        )

        total_normal = news_es.count_search_main(
            index_name="vosint",
            query=query,
            gte=params["start_date"],
            lte=params["end_date"],
            lang=params["language_source"],
            sentiment="0"
            if params["sentiment"] == "" or params["sentiment"] == "0"
            else 9999,
        )

    else:
        # Get total documents
        total_docs = await client.count_documents(filter_spec)

        # Get total sentiments
        check_array = filter_spec.get("$and") or []
        # Remove the object with the specified field
        removed_object = None
        updated_conditions = []
        for condition in check_array:
            if "data:class_sacthai" in condition:
                removed_object = condition
            else:
                updated_conditions.append(condition)

        total_positive = await client.count_documents(
            {
                **filter_spec,
                **{"$and": [*updated_conditions, {"data:class_sacthai": "9999"}]},
            }
            if any(
                "data:class_sacthai" in obj and obj["data:class_sacthai"] != "1"
                for obj in check_array
            )
            else {
                **filter_spec,
                **{"$and": [*updated_conditions, {"data:class_sacthai": "1"}]},
            }
        )
        total_negative = await client.count_documents(
            {
                **filter_spec,
                **{"$and": [*updated_conditions, {"data:class_sacthai": "9999"}]},
            }
            if any(
                "data:class_sacthai" in obj and obj["data:class_sacthai"] != "2"
                for obj in check_array
            )
            else {
                **filter_spec,
                **{"$and": [*updated_conditions, {"data:class_sacthai": "2"}]},
            }
        )
        total_normal = await client.count_documents(
            {
                **filter_spec,
                **{"$and": [*updated_conditions, {"data:class_sacthai": "9999"}]},
            }
            if any(
                "data:class_sacthai" in obj and obj["data:class_sacthai"] != "0"
                for obj in check_array
            )
            else {
                **filter_spec,
                **{"$and": [*updated_conditions, {"data:class_sacthai": "0"}]},
            }
        )

    total_sentiments = {
        "total_positive": total_positive,
        "total_negative": total_negative,
        "total_normal": total_normal,
    }

    return {"total_records": total_docs, "total_sentiments": total_sentiments}


async def count_ttxvn(filter_spec, params):
    total_docs = news_es.count_search_main_ttxvn(
        index_name="vosint_ttxvn",
        query=params["text_search"],
        gte=params["start_date"] or None,
        lte=params["end_date"] or None,
        # lang=params["language_source"],
        # sentiment=params["sentiment"],
    )

    return {"total_records": total_docs}


def read_ttxvn(news_ids: List[str], user_id):
    news_ids_list = [ObjectId(news_id) for news_id in news_ids]
    filter_spec = {
        "_id": {"$in": news_ids_list},
        "list_user_read": {"$not": {"$all": [user_id]}},
    }
    update_command = {"$push": {"list_user_read": user_id}}
    collection = "ttxvn"
    return MongoRepository().update_many(collection, filter_spec, update_command)


def unread_ttxvn(news_ids: List[str], user_id):
    news_ids_list = [ObjectId(news_id) for news_id in news_ids]
    filter_spec = {"_id": {"$in": news_ids_list}}
    update_command = {"$pull": {"list_user_read": {"$in": [user_id]}}}
    collection = "ttxvn"
    return MongoRepository().update_many(collection, filter_spec, update_command)
