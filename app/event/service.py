import asyncio
import random
from datetime import datetime
from typing import List

import pydantic
from bson.objectid import ObjectId
from fastapi import HTTPException, status

from app.event.model import AddNewEvent, CreateEvent
from app.news.services import find_news_by_filter
from app.report.service import find_report_by_filter
from db.init_db import get_collection_client
from vosint_ingestion.models import MongoRepository
import re

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

client = get_collection_client("event")
client2 = get_collection_client("News")
client3 = get_collection_client("events")
report_client = get_collection_client("report")

projection = {"_id": True, "data:title": True, "data:url": True}
projection_rp = {"_id": True, "title": True}


async def add_event(event):
    if event["system_created"] == True:
        created_event = await client3.insert_one(event, {"user_id": 0})
        id_event = str(created_event.inserted_id)
        filter_event = await client3.find_one({"_id": ObjectId(id_event)})
        event_name = filter_event["event_name"]
        newsList = event.get("new_list", [])
        listReport = event.get("list_report", [])
        await client2.update_many(
            {"_id": {"$in": [ObjectId(event_id) for event_id in newsList]}},
            {
                "$addToSet": {
                    "event_list": {"event_id": id_event, "event_name": event_name}
                }
            },
        )
        await report_client.update_many(
            {"_id": {"$in": [ObjectId(report_id) for report_id in listReport]}},
            {"$addToSet": {"event_list": id_event}},
        )
        return created_event

    if event["system_created"] == False:
        created_event = await client.insert_one(event)
        id_event = str(created_event.inserted_id)
        filter_event = await client.find_one({"_id": ObjectId(id_event)})
        event_name = filter_event["event_name"]
        newsList = event.get("new_list", [])
        listReport = event.get("list_report", [])
        await client2.update_many(
            {"_id": {"$in": [ObjectId(event_id) for event_id in newsList]}},
            {
                "$addToSet": {
                    "event_list": {"event_id": id_event, "event_name": event_name}
                }
            },
        )
        await report_client.update_many(
            {"_id": {"$in": [ObjectId(report_id) for report_id in listReport]}},
            {"$addToSet": {"event_list": id_event}},
        )
        return created_event


async def get_all_by_paginate(filter, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_event = []

    async for item in client.find(filter).sort("_id").skip(offset).limit(limit):
        ll = []
        ls_rp = []
        for Item in item["new_list"]:
            id_new = {"_id": ObjectId(Item)}
            async for new in client2.find(id_new, projection):
                gg = json(new)
                ll.append(gg)
        for Item2 in item["list_report"]:
            id_report = {"_id": ObjectId(Item2)}
            async for rp in report_client.find(id_report, projection_rp):
                reports = json(rp)
                ls_rp.append(reports)
        item["new_list"] = ll
        item["list_report"] = ls_rp
        item["date_created"] = str(item["date_created"])
        item["total_new"] = len(item["new_list"])
        item = json(item)
        list_event.append(item)
    return list_event


async def get_all_by_system(filter, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_event = []

    async for item in client3.find(filter).sort("_id").skip(offset).limit(limit):
        # ll = []
        # for Item in item["new_list"]:
        #     id_new = {"_id": ObjectId(Item)}
        #     async for new in client2.find(id_new, projection):
        #         gg = json(new)
        #         ll.append(gg)
        # item["date_created"] = str(item["date_created"])
        # item["new_list"] = ll
        # item["total_new"] = len(item["new_list"])
        item["date_created"] = str(item["date_created"])
        item = json(item)
        list_event.append(item)
    return list_event


def json(event) -> dict:
    event["_id"] = str(event["_id"])
    return event


async def search_id(user_id: str):
    query = {"user_id": {"$eq": user_id}}
    list_event = []
    async for item in client.find(query).sort("_id"):
        ll = []
        ls_rp = []
        for Item in item["new_list"]:
            id_new = {"_id": ObjectId(Item)}
            async for new in client2.find(id_new, projection):
                gg = json(new)
                ll.append(gg)
        for Item2 in item["list_report"]:
            id_report = {"_id": ObjectId(Item2)}
            async for rp in report_client.find(id_report, projection_rp):
                reports = json(rp)
                ls_rp.append(reports)
        item["list_report"] = ls_rp
        item["date_created"] = str(item["date_created"])
        item["new_list"] = ll
        item["total_new"] = len(item["new_list"])
        item = json(item)
        list_event.append(item)
    return list_event


async def get_chu_khach(user_id: str, text, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_ck = []
    query = {}
    unique = set()

    # if user_id:
    #     query["user_id"] = user_id

    if text:
        query["$or"] = [{"name": {"$regex": text, "$options": "i"}}]

    object_client = get_collection_client("object")

    async for item in object_client.find(query, projection={"_id": 1, "name": 1}).sort(
        "_id"
    ).skip(offset).limit(limit):
        item["_id"] = str(item["_id"])
        list_ck.append(item)

    # if text:
    #     query["$or"] = [
    #         {"chu_the": {"$regex": text, "$options": "i"}},
    #         {"khach_the": {"$regex": text, "$options": "i"}},
    #     ]

    # async for item in client3.find(query).sort("_id").skip(offset).limit(limit):
    # item["date_created"] = str(item["date_created"])
    # obj = {"_id": str(item["_id"]) + "0", "name": item["khach_the"]}
    # obj1 = {"_id": str(item["_id"]) + "1", "name": item["chu_the"]}
    # name = obj["name"]
    # if name not in unique and name != "":
    #     unique.add(name)
    #     list_ck.append(obj)

    # name = obj1["name"]
    # if name not in unique and name != "":
    #     unique.add(name)
    #     list_ck.append(obj1)

    return list_ck


projection_event_system = {
    "_id": True,
    "event_name": True,
    "event_content": True,
    "date_created": True,
    "chu_the": True,
    "khach_the": True,
    "sentiment": True,
    "new_list": True,
}


async def search_chu_khach(
    user_id: str,
    chu_the,
    khach_the,
    start_date: str,
    end_date: str,
    skip: int,
    limit: int,
):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_ev = []
    query = {}
    if start_date and end_date:
        _start_date = datetime.strptime(start_date, "%d/%m/%Y")
        _end_date = datetime.strptime(end_date, "%d/%m/%Y")
        query = {"date_created": {"$gte": _start_date, "$lte": _end_date}}

    if chu_the and khach_the:
        query["$or"] = [
            {
                "$and": [
                    {"chu_the": chu_the},
                    {"khach_the": khach_the},
                ]
            },
            {
                "$and": [
                    {"chu_the": khach_the},
                    {"khach_the": chu_the},
                ]
            },
        ]

    else:
        if chu_the:
            query["$or"] = [{"chu_the": chu_the}, {"khach_the": chu_the}]
        if khach_the:
            query["$or"] = [{"chu_the": khach_the}, {"khach_the": khach_the}]
    # if user_id:
    #     query["user_id"] = user_id

    async for item in client3.find(query, projection_event_system).sort(
        "date_created", -1
    ).skip(offset).limit(limit):
        # print(item)
        current_source = []
        check_key = "new_list"
        condition = (
            check_key in item
            and isinstance(item["new_list"], list)
            and len(item["new_list"]) >= 1
        )
        if condition:
            for _id in item["new_list"]:
                async for news in client2.find({"_id": ObjectId(_id)}, projection):
                    current_news = json(news)
                    current_source.append(current_news)

        # ll = []
        # ls_rp = []
        # for Item in item["new_list"]:
        #     id_new = {"_id": ObjectId(Item)}
        #     async for new in client2.find(id_new, projection):
        #         gg = json(new)
        #         ll.append(gg)
        # for Item2 in item["list_report"]:
        #     id_report = {"_id": ObjectId(Item2)}
        #     async for rp in report_client.find(id_report, projection_rp):
        #         reports = json(rp)
        #         ls_rp.append(reports)
        # item["new_list"] = ll
        # item["list_report"] = ls_rp
        item["new_list"] = current_source
        item["date_created"] = str(item["date_created"])
        # item["total_new"] = len(item["new_list"])
        item = json(item)
        list_ev.append(item)
    return list_ev


async def count_chu_khach(chu_the, khach_the, start_date, end_date, user_id):
    query = {}
    conditions = []
    if start_date and end_date:
        _start_date = datetime.strptime(start_date, "%d/%m/%Y")
        _end_date = datetime.strptime(end_date, "%d/%m/%Y")
        conditions.append({"date_created": {"$gte": _start_date, "$lte": _end_date}})
    if chu_the and khach_the:
        conditions.append(
            {
                "$or": [
                    {
                        "$and": [
                            {"chu_the": chu_the},
                            {"khach_the": khach_the},
                        ]
                    },
                    {
                        "$and": [
                            {"chu_the": khach_the},
                            {"khach_the": chu_the},
                        ]
                    },
                ]
            }
        )
    else:
        if chu_the:
            query["$or"] = [{"chu_the": chu_the}, {"khach_the": chu_the}]
        if khach_the:
            query["$or"] = [{"chu_the": khach_the}, {"khach_the": khach_the}]

    # if user_id:
    #     conditions.append({"user_id": user_id})
    if conditions:
        query["$and"] = conditions
    return await client3.count_documents(query)


async def search_event(
    event_name: str,
    data: ObjectId,
    start_date: str,
    end_date: str,
    user_id,
    system_created,
    skip: int,
    limit: int,
):
    # fields_search = {
    #     "_id": 1,
    #     "event_content": 1,
    #     "event_name": 1,
    #     "sentiment": 1,
    #     "title_translate": 1,
    #     "content_translate": 1,
    #     "date_created": 1,
    #     "list_user_read": 1,
    #     "news_added_by_user": 1,
    # }

    fields_search = {
        "data:summaries": False,
        "embedding_title": False,
        "embedding_content": False,
    }

    offset = (skip - 1) * limit if skip > 0 else 0
    list_event = []
    query = {}

    if start_date and end_date:
        _start_date = datetime.strptime(start_date, "%d/%m/%Y")
        _end_date = datetime.strptime(end_date, "%d/%m/%Y")
        query = {"date_created": {"$gte": _start_date, "$lte": _end_date}}
    if event_name:
        query["$or"] = [
            {"event_name": {"$regex": event_name, "$options": "i"}},
            {"chu_the": {"$regex": event_name, "$options": "i"}},
            {"khach_the": {"$regex": event_name, "$options": "i"}},
        ]
    if data:
        query["new_list"] = {"$nin": [data]}
    if not query:
        query = {}
    if system_created == False:
        if user_id:
            query["user_id"] = user_id

        query["system_created"] = {"$ne": True}
        async for item in client.find(query, fields_search).sort("date_created", -1).skip(
            offset
        ).limit(limit):
            # ll = []
            ls_rp = []
            # for Item in item["new_list"]:
            #     id_new = {"_id": ObjectId(Item)}
            #     async for new in client2.find(id_new, projection):
            #         gg = json(new)
            #         ll.append(gg)
            if "list_report" in item:
                for Item2 in item["list_report"]:
                    id_report = {"_id": ObjectId(Item2)}
                    async for rp in report_client.find(id_report, projection_rp):
                        reports = json(rp)
                        ls_rp.append(reports)
            # item["new_list"] = ll
            item["list_report"] = ls_rp
            item["date_created"] = str(item["date_created"])
            item["total_new"] = len(item["new_list"])
            items = json(item)
            list_event.append(items)

    if system_created == True:
        detect_condition = {
            '$and': [
                {
                    '$or': [
                        {'display': {'$exists': False}}, 
                        {'display': True}, 
                    ]
                },
            ]
        }

        # query.setdefault('$and', []).extend(detect_condition['$and'])
        query.update(detect_condition)

        async for item3 in client3.find(query, fields_search).sort("date_created", -1).skip(
            offset
        ).limit(limit):
            # ll = []
            # ls_rp = []
            # for Item in item3["new_list"]:
            #     id_new = {"_id": ObjectId(Item)}
            #     async for new in client2.find(id_new, projection):
            #         gg = json(new)
            #         ll.append(gg)
            # if "list_report" in item3:
            #     for Item2 in item3["list_report"]:
            #         id_report = {"_id": ObjectId(Item2)}
            #         async for rp in report_client.find(id_report, projection_rp):
            #             reports = json(rp)
            #             ls_rp.append(reports)
            # # item3["new_list"] = ll
            # item3["list_report"] = ls_rp

            item3["_id"] = str(item3["_id"])
            item3["date_created"] = str(item3["date_created"])
            # if "list_user_clone" not in item3:
            #     await client.aggregate(
            #         [{"$addFields": {"list_user_clone": []}}]
            #     ).to_list(length=None)
            list_event.append(item3)

    list_fields = [
        "chu_the",
        "created_at",
        "khach_the",
        "list_linh_vuc",
        # "list_report",
        "location",
        "modified_at",
        "new_list",
    ]

    limit_string = 270

    for record in list_event:
        try:
            record["event_content"] = record["event_content"][0:limit_string]
            if(record.get("event_translate")):
                record["event_translate"] = record["event_translate"][0:limit_string]
        except:
            pass
        for key in list_fields:
            record.pop(key, None)

    return list_event


async def search_result(name, id_new, start_date, end_date, user_id, system_created):
    query = {}
    conditions = []

    if system_created == False:
        if name:
            conditions.append(
                {
                    "$or": [
                        {"event_name": {"$regex": name, "$options": "i"}},
                        {"chu_the": {"$regex": name, "$options": "i"}},
                        {"khach_the": {"$regex": name, "$options": "i"}},
                    ]
                }
            )

        if id_new:
            conditions.append({"new_list": {"$nin": [id_new]}})

        if start_date and end_date:
            _start_date = datetime.strptime(start_date, "%d/%m/%Y")
            _end_date = datetime.strptime(end_date, "%d/%m/%Y")
            conditions.append(
                {"date_created": {"$gte": _start_date, "$lte": _end_date}}
            )

        if user_id:
            conditions.append({"user_id": user_id})

        conditions.append({"system_created": {"$ne": True}})

        if conditions:
            query["$and"] = conditions

        return await client.count_documents(query)

    if system_created == True:
        if name:
            conditions.append(
                {
                    "$or": [
                        {"event_name": {"$regex": name, "$options": "i"}},
                        {"chu_the": {"$regex": name, "$options": "i"}},
                        {"khach_the": {"$regex": name, "$options": "i"}},
                    ]
                }
            )

        if id_new:
            conditions.append({"new_list": {"$nin": [id_new]}})

        if start_date and end_date:
            _start_date = datetime.strptime(start_date, "%d/%m/%Y")
            _end_date = datetime.strptime(end_date, "%d/%m/%Y")
            conditions.append(
                {"date_created": {"$gte": _start_date, "$lte": _end_date}}
            )

        if conditions:
            query["$and"] = conditions

        return await client3.count_documents(query)


async def event_detail(id) -> dict:
    ev_detail = await client.find_one({"_id": ObjectId(id)})
    new_list = []
    if ev_detail is None:
        ev_detail = await client3.find_one({"_id": ObjectId(id)})
        if ev_detail is None:
            return None

    if "new_list" in ev_detail:
        new_list = await find_news_by_filter(
            {"_id": {"$in": convert_map_str_to_object_id(ev_detail["new_list"])}},
            {"_id": 1, "data:title": 1, "data:url": 1},
        )
        ev_detail["new_list"] = new_list

    if "list_report" in ev_detail:
        ls_rp = await find_report_by_filter(
            {"_id": {"$in": convert_map_str_to_object_id(ev_detail["list_report"])}},
            {"_id": 1, "title": 1},
        )
        ev_detail["list_report"] = ls_rp

    if ev_detail:
        ev_detail["total_new"] = len(ev_detail["new_list"])
        ev = json(ev_detail)
        return ev


async def get_by_new_id(new_id) -> dict:
    list_event = []

    async def process_item(item):
        ll = []
        ls_rp = []
        for Item in item["new_list"]:
            id_new = {"_id": ObjectId(Item)}
            async for new in client2.find(id_new, projection):
                gg = json(new)
                ll.append(gg)
        for Item2 in item["list_report"]:
            id_report = {"_id": ObjectId(Item2)}
            async for rp in report_client.find(id_report, projection_rp):
                reports = json(rp)
                ls_rp.append(reports)
        item["new_list"] = ll
        item["list_report"] = ls_rp
        item["date_created"] = str(item["date_created"])
        item["total_new"] = len(item["new_list"])
        item = json(item)
        list_event.append(item)

    async for item in client.find({"new_list": new_id}).sort("_id"):
        await process_item(item)

    async for item in client3.find({"new_list": new_id}).sort("_id"):
        await process_item(item)

    return list_event


async def get_system_by_new_id(new_id) -> dict:
    list_event = []

    async for item in client3.find({"new_list": new_id}).sort("_id"):
        ll = []
        ls_rp = []
        for Item in item["new_list"]:
            id_new = {"_id": ObjectId(Item)}
            async for new in client2.find(id_new, projection):
                gg = json(new)
                ll.append(gg)
        for Item2 in item["list_report"]:
            id_report = {"_id": ObjectId(Item2)}
            async for rp in report_client.find(id_report, projection_rp):
                reports = json(rp)
                ls_rp.append(reports)
        item["new_list"] = ll
        item["list_report"] = ls_rp
        item["date_created"] = str(item["date_created"])
        item["total_new"] = len(item["new_list"])
        item = json(item)
        list_event.append(item)
    return list_event


async def event_detail_system(id) -> dict:
    ev_detail = await client3.find_one({"_id": ObjectId(id)})
    new_list = []
    if "new_list" in ev_detail:
        new_list = await find_news_by_filter(
            {"_id": {"$in": convert_map_str_to_object_id(ev_detail["new_list"])}},
            {"_id": 1, "data:title": 1, "data:url": 1},
        )
        ev_detail["new_list"] = new_list
    if ev_detail:
        ev_detail["total_new"] = len(ev_detail["new_list"])
        ev = json(ev_detail)
        return ev


def convert_map_str_to_object_id(array: List[str]):
    return list(map(ObjectId, array))


async def count_event(count):
    return await client.count_documents(count)


async def count_event_system(count):
    return await client3.count_documents(count)


async def update_add(id: str, data):
    event = await client.find_one({"_id": ObjectId(id)})
    if event:
        event_name = event["event_name"]
        newsList = data.get("new_list", [])
        exist_event = await client.find_one({"event_name": data["event_name"]})
        if exist_event:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="event already exist"
            )
        await client.insert_one(data)
        await client2.update_many(
            {"event_list.event_id": id, "event_list.event_name": event_name},
            {"$pull": {"event_list": {"event_id": id, "event_name": event_name}}},
        )
        for new in newsList:
            new_id = new
            await client2.update_one(
                {"_id": ObjectId(new_id)},
                {
                    "$addToSet": {
                        "event_list": {"event_id": id, "event_name": event_name}
                    }
                },
            )


async def update_add_system(id: str, data):
    event_2 = await client3.find_one({"_id": ObjectId(id)})
    if event_2:
        event_name_2 = event_2["event_name"]
        newsList_2 = data.get("new_list", [])
        exist_event_2 = await client3.find_one({"event_name": data["event_name"]})
        if exist_event_2:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="event already exist"
            )
        await client.insert_one(data)
        await client2.update_many(
            {"event_list.event_id": id, "event_list.event_name": event_name_2},
            {"$pull": {"event_list": {"event_id": id, "event_name": event_name_2}}},
        )
        for new in newsList_2:
            new_id = new
            await client2.update_one(
                {"_id": ObjectId(new_id)},
                {
                    "$addToSet": {
                        "event_list": {"event_id": id, "event_name": event_name_2}
                    }
                },
            )


async def update_event(id: str, data: dict):
    id_event = str(id)
    event = await client.find_one({"_id": ObjectId(id)})
    event_2 = await client3.find_one({"_id": ObjectId(id)})

    # list_event_1 = await client.find(
    #     {}, projection={"_id": 1, "event_name": 1, "system_created": 1}
    # ).to_list(length=None)
    # list_event_2 = await client3.find(
    #     {}, projection={"_id": 1, "event_name": 1, "system_created": 1}
    # ).to_list(length=None)

    if event:
        event_name = event["event_name"]
        newsList = data.get("new_list", [])
        reportList = data.get("list_report", [])

        await client2.update_many(
            {"event_list.event_id": id_event, "event_list.event_name": event_name},
            {"$pull": {"event_list": {"event_id": id_event, "event_name": event_name}}},
        )
        # for new in newsList:
        #     new_id = new
        news_ids = [ObjectId(_id) for _id in newsList]

        await client2.update_many(
            # {"_id": ObjectId(new_id)},
            {"_id": {"$in": news_ids}},
            {
                "$addToSet": {
                    "event_list": {"event_id": id_event, "event_name": event_name}
                }
            },
        )

        # await report_client.update_many(
        #     {"event_list": id_event},
        #     {"$pull": {"event_list": {"$in": [id_event]}}},
        # )

        # for rp in reportList:
        #     rp_id = rp
        report_ids = [ObjectId(_id) for _id in reportList]
        await report_client.update_many(
            # {"_id": ObjectId(rp_id)}, {"$addToSet": {"event_list": id_event}}
            {"_id": {"$in": report_ids}},
            {"$addToSet": {"event_list": id_event}},
        )

        check_dup = await client.find(
            {
                "event_name": data["event_name"],
                "system_created": event.get("system_created"),
            }
        ).to_list(None)
        if len(check_dup) > 1 and data["system_created"] != True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="event is duplicated"
            )

        # for item in list_event_1:
        #     if (
        #         item["_id"] != event["_id"]
        #         and item["event_name"] == data["event_name"]
        #         and (item.get("system_created") == event["system_created"])
        #         and data["system_created"] != True
        #     ):
        #         raise HTTPException(
        #             status_code=status.HTTP_409_CONFLICT, detail="event is duplicated"
        #         )

        updated_event = await client.update_one({"_id": ObjectId(id)}, {"$set": data})
        if updated_event:
            return status.HTTP_200_OK
        return False

    if event_2:
        event_name_2 = event_2["event_name"]
        newsList = data.get("new_list", [])

        await client2.update_many(
            {"event_list.event_id": id_event, "event_list.event_name": event_name_2},
            {
                "$pull": {
                    "event_list": {"event_id": id_event, "event_name": event_name_2}
                }
            },
        )
        for new in newsList:
            new_id = new
            await client2.update_one(
                {"_id": ObjectId(new_id)},
                {
                    "$addToSet": {
                        "event_list": {"event_id": id_event, "event_name": event_name_2}
                    }
                },
            )

        await report_client.update_many(
            {"event_list": id_event},
            {"$pull": {"event_list": {"$in": [id_event]}}},
        )
        for rp in reportList:
            rp_id = rp
            await report_client.update_one(
                {"_id": ObjectId(rp_id)}, {"$addToSet": {"event_list": id_event}}
            )

        check_dup = await client3.find(
            {
                "event_name": data["event_name"],
                "system_created": event.get("system_created"),
            }
        ).to_list(None)

        if len(check_dup) > 1 and data["system_created"] != True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="event is duplicated"
            )
        # for item in list_event_2:
        #     if (
        #         item["_id"] != event_2["_id"]
        #         and item["event_name"] == data["event_name"]
        #         and (item.get("system_created") == event["system_created"])
        #         and data["system_created"] != True
        #     ):
        #         raise HTTPException(
        #             status_code=status.HTTP_409_CONFLICT, detail="event is duplicated"
        #         )

        updated_event = await client3.update_one({"_id": ObjectId(id)}, {"$set": data})
        if updated_event:
            return status.HTTP_200_OK
        return False


async def add_list_new_id(id: str, id_new: List[ObjectId]):
    id_event = str(id)
    filter_event = await client3.find_one({"_id": ObjectId(id_event)})
    filter_event_2 = await client.find_one({"_id": ObjectId(id_event)})

    if filter_event:
        event_name = filter_event["event_name"]
        newList = []
        for item in id_new:
            newList.append(item)
        await client2.update_many(
            {"_id": {"$in": [ObjectId(event_id) for event_id in newList]}},
            {
                "$addToSet": {
                    "event_list": {"event_id": id_event, "event_name": event_name}
                }
            },
        )
        return await client3.update_one(
            {"_id": ObjectId(id)}, {"$push": {"new_list": {"$each": id_new}}}
        )
    if filter_event_2:
        event_name_2 = filter_event_2["event_name"]
        newList = []
        for item in id_new:
            newList.append(item)
        await client2.update_many(
            {"_id": {"$in": [ObjectId(event_id) for event_id in newList]}},
            {
                "$addToSet": {
                    "event_list": {"event_id": id_event, "event_name": event_name_2}
                }
            },
        )
        return await client.update_one(
            {"_id": ObjectId(id)}, {"$push": {"new_list": {"$each": id_new}}}
        )


async def add_list_event_id(id_new: str, list_id_event: List[ObjectId]):
    id_news = str(id_new)
    eventList = []
    for item in list_id_event:
        eventList.append(item)

    event_ids = [ObjectId(event_id) for event_id in list_id_event]
    ev_name = await client.find({"_id": {"$in": event_ids}}).to_list(length=None)
    ev_name_2 = await client3.find({"_id": {"$in": event_ids}}).to_list(length=None)

    for item2 in ev_name_2:
        if item2:
            ev_id_2 = str(item2["_id"])
            await client2.update_many(
                {"_id": ObjectId(id_news)},
                {
                    "$addToSet": {
                        "event_list": {
                            "event_id": ev_id_2,
                            "event_name": item2["event_name"],
                        }
                    }
                },
            ),
            await client3.update_many(
                {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}},
                {"$addToSet": {"new_list": id_news}},
            )
    for item in ev_name:
        if item:
            ev_id = str(item["_id"])
            await client2.update_many(
                {"_id": ObjectId(id_news)},
                {
                    "$addToSet": {
                        "event_list": {
                            "event_id": ev_id,
                            "event_name": item["event_name"],
                        }
                    }
                },
            ),
            await client.update_many(
                {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}},
                {"$addToSet": {"new_list": id_news}},
            ),
        for item2 in ev_name_2:
            if item2:
                ev_id_2 = str(item2["_id"])
                await client2.update_many(
                    {"_id": ObjectId(id_news)},
                    {
                        "$addToSet": {
                            "event_list": {
                                "event_id": ev_id_2,
                                "event_name": item2["event_name"],
                            }
                        }
                    },
                ),
                await client3.update_many(
                    {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}},
                    {"$addToSet": {"new_list": id_news}},
                )
            if item and item2:
                ev_id = str(item["_id"])
                ev_id_2 = str(item2["_id"])
                await asyncio.gather(
                    client3.update_many(
                        {
                            "_id": {
                                "$in": [ObjectId(event_id) for event_id in eventList]
                            }
                        },
                        {"$addToSet": {"new_list": id_news}},
                    ),
                    client.update_many(
                        {
                            "_id": {
                                "$in": [ObjectId(event_id) for event_id in eventList]
                            }
                        },
                        {"$addToSet": {"new_list": id_news}},
                    ),
                    client2.update_many(
                        {"_id": ObjectId(id_news)},
                        {
                            "$addToSet": {
                                "event_list": {
                                    "$each": [
                                        {
                                            "event_id": ev_id,
                                            "event_name": item["event_name"],
                                        },
                                        {
                                            "event_id": ev_id_2,
                                            "event_name": item2["event_name"],
                                        },
                                    ]
                                }
                            }
                        },
                    ),
                )


async def remove_list_new_id(id: str, id_new: List[ObjectId]):
    id_event = str(id)
    filter_event = await client3.find_one({"_id": ObjectId(id_event)})
    filter_event_2 = await client.find_one({"_id": ObjectId(id_event)})

    if filter_event:
        event_name = filter_event["event_name"]
        newList = []
        for item in id_new:
            newList.append(item)
        await client2.update_many(
            {"event_list.event_id": id_event, "event_list.event_name": event_name},
            {"$pull": {"event_list": {"event_id": id_event, "event_name": event_name}}},
        )
        return await client3.update_one(
            {"_id": ObjectId(id)}, {"$pull": {"new_list": {"$in": id_new}}}
        )
    if filter_event_2:
        event_name_2 = filter_event_2["event_name"]
        newList = []
        for item in id_new:
            newList.append(item)
        await client2.update_many(
            {"event_list.event_id": id_event, "event_list.event_name": event_name_2},
            {
                "$pull": {
                    "event_list": {"event_id": id_event, "event_name": event_name_2}
                }
            },
        )
        return await client.update_one(
            {"_id": ObjectId(id)}, {"$pull": {"new_list": {"$in": id_new}}}
        )


async def remove_list_event_id(id: str, list_id_event: List[ObjectId]):
    id_new = str(id)
    eventList = []
    for item in list_id_event:
        eventList.append(item)
    ev_name = await client.find_one(
        {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}}
    )
    ev_name_2 = await client3.find_one(
        {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}}
    )
    if ev_name_2:
        ev_id_2 = str(ev_name_2["_id"])
        await client2.update_many(
            {
                "event_list.event_id": ev_id_2,
                "event_list.event_name": ev_name_2["event_name"],
            },
            {
                "$pull": {
                    "event_list": {
                        "event_id": ev_id_2,
                        "event_name": ev_name_2["event_name"],
                    }
                }
            },
        )
        return await client3.update_one(
            {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}},
            {"$pull": {"new_list": id_new}},
        )
    if ev_name:
        ev_id = str(ev_name["_id"])
        await client2.update_many(
            {
                "event_list.event_id": ev_id,
                "event_list.event_name": ev_name["event_name"],
            },
            {
                "$pull": {
                    "event_list": {
                        "event_id": ev_id,
                        "event_name": ev_name["event_name"],
                    }
                }
            },
        )
        return await client.update_one(
            {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}},
            {"$pull": {"new_list": id_new}},
        )


async def add_list_new(id: str, data: List[AddNewEvent]):
    list_ev = []
    for Data in data:
        list_ev.append(
            {
                "id_new": Data.id_new,
                "data_title": Data.data_title,
                "data_url": Data.data_url,
            }
        )
    return await client.update_one(
        {"_id": ObjectId(id)},
        {"$addToSet": {"new_list": {"$each": [Data.dict() for Data in data]}}},
    )


async def delete_list_new(id: str, data: List[AddNewEvent]):
    docs = [dict(Data) for Data in data]
    return await client.update_one(
        {"_id": ObjectId(id)}, {"$pull": {"new_list": {"$in": docs}}}
    )


async def delete_event(id, user_id):
    id_event = str(id)
    event = await client.find_one({"_id": ObjectId(id)})
    event_2 = await client3.find_one({"_id": ObjectId(id)})

    if event:
        event_name = event["event_name"]
        await client2.update_many(
            {"event_list.event_id": id_event, "event_list.event_name": event_name},
            {"$pull": {"event_list": {"event_id": id_event, "event_name": event_name}}},
        )
        await report_client.update_many(
            {"event_list": id_event},
            {"$pull": {"event_list": {"$in": [id_event]}}},
        )
        await client.delete_one({"_id": ObjectId(id)})
        await client3.update_one(
            {"_id": ObjectId(id_event)},
            {
                "$pull": {"list_user_clone": {"$in": [user_id]}},
            },
        )
        return 200
    if event_2:
        event_name_2 = event_2["event_name"]
        await client2.update_many(
            {"event_list.event_id": id_event, "event_list.event_name": event_name_2},
            {
                "$pull": {
                    "event_list": {"event_id": id_event, "event_name": event_name_2}
                }
            },
        )
        await report_client.update_many(
            {"event_list": id_event},
            {"$pull": {"event_list": {"$in": [id_event]}}},
        )
        await client3.delete_one({"_id": ObjectId(id)})
        return 200


async def get_events_by_ids(ids: List[str]):
    list_obj_ids = []
    for event_id in ids:
        list_obj_ids.append(ObjectId(event_id))
    events = []
    async for event in client3.find({"_id": {"$in": list_obj_ids}}):
        events.append(event)
    return events


async def get_news_by_ids(ids: List[str]):
    list_obj_ids = []
    for event_id in ids:
        list_obj_ids.append(ObjectId(event_id))
    news = {}
    async for doc in client2.find({"_id": {"$in": list_obj_ids}}):
        news[str(doc["_id"])] = f"({doc['source_host_name']}) {doc['data:title']}"
    return news


def check_read_events(event_ids: List[str], user_id, is_system_created=True):
    event_id_list = [ObjectId(event_id) for event_id in event_ids]
    filter_spec = {
        "_id": {"$in": event_id_list},
        "list_user_read": {"$not": {"$all": [user_id]}},
    }
    update_command = {"$push": {"list_user_read": user_id}}
    collection = "events" if is_system_created == True else "event"
    return MongoRepository().update_many(collection, filter_spec, update_command)


def un_check_read_events(event_ids: List[str], user_id, is_system_created=True):
    event_id_list = [ObjectId(event_id) for event_id in event_ids]
    filter_spec = {"_id": {"$in": event_id_list}}
    update_command = {"$pull": {"list_user_read": {"$in": [user_id]}}}
    collection = "events" if is_system_created == True else "event"
    return MongoRepository().update_many(collection, filter_spec, update_command)


def get_countries():
    countries, _ = MongoRepository().get_many("object", {"object_type": "Quốc gia"})
    result_dict = {}
    for country in countries:
        result_dict[country["name"]] = 1
    return result_dict


def process_source_target(value: str, country_dict, country_regex):
    if "," not in value and country_dict.get(value) != None:
        return value
    if "," not in value and country_dict.get(value) == None:
        match = re.findall(country_regex, value)
        if len(match) > 0:
            return match[0]
        return ""
    result = []
    data = [r.strip() for r in value.split(",")]
    for row in data:
        val = row
        if country_dict.get(val) == None:
            match = re.findall(country_regex, val)
            if len(match) > 0:
                val = match[0]
        if country_dict.get(val) != None:
            result.append(val)
    return result


def process_duplicate_source_target(source, target):
    target_dict = {}
    if type(target) == str:
        target = [target]
    for country in target:
        target_dict[country] = 1
    if type(source) == str:
        source = [source]
    for country in source:
        if target_dict.get(country) != None:
            target_dict.pop(country)
    return list(target_dict.keys())


def create_source_target_pair(source, target):
    pairs = []
    if type(source) == str:
        source = [source]
    if type(target) == str:
        target = [target]
    # Sử dụng hai vòng lặp để tạo các cặp
    for country1 in source:
        for country2 in target:
            if country1 != country2:
                pairs.append((country1, country2))
    return pairs


def group_edges_by_pair(data):
    data_dict = {}
    for row in data.get("edges"):
        if data_dict.get(row["source"] + row["target"]) == None:
            data_dict[row["source"] + row["target"]] = []
        data_dict[row["source"] + row["target"]].append(row)
    result = []
    for key_pair in list(data_dict.keys()):
        edge_data = data_dict.get(key_pair)
        sum_edge = {
            "source": "Ukraine",
            "target": "Nga",
            "positive": 0,
            "normal": 0,
            "negative": 0,
            "total": 0,
        }

        for edge in edge_data:
            if sum_edge == None:
                sum_edge = edge.copy()
                continue
            else:
                sum_edge["source"] = edge["source"]
                sum_edge["target"] = edge["target"]
                sum_edge["normal"] += edge["normal"]
                sum_edge["positive"] += edge["positive"]
                sum_edge["negative"] += edge["negative"]
                sum_edge["total"] += edge["total"]
        result.append(sum_edge.copy())
    return result


def get_graph_data(object_ids, start_date, end_date):
    object_filter = [ObjectId(object_id) for object_id in object_ids]
    objects, _ = MongoRepository().get_many(
        "object",
        {"_id": {"$in": object_filter}},
        projection={"name": 1, "avatar_url": 1},
    )
    object_names = [object["name"] for object in objects]
    regex = "|".join(object_names)
    object_image_dict = {}
    countries_dict = get_countries()
    country_regex = "|".join(list(countries_dict.keys()))
    for object in objects:
        object_image_dict[object["name"]] = object["avatar_url"]
    pipeline = [
        {
            "$match": {
                "$and": [
                    {"chu_the": {"$regex": regex}},
                    {"khach_the": {"$regex": regex}},
                ]
            }
        },
        {
            "$project": {
                "khach_the": 1,
                "chu_the": 1,
                "normal": {"$cond": [{"$eq": ["$sentiment", "0"]}, 1, 0]},
                "negative": {"$cond": [{"$eq": ["$sentiment", "2"]}, 1, 0]},
                "positive": {"$cond": [{"$eq": ["$sentiment", "1"]}, 1, 0]},
            }
        },
        {
            "$group": {
                "_id": {"source": "$chu_the", "target": "$khach_the"},
                "normal": {"$sum": "$normal"},
                "negative": {"$sum": "$negative"},
                "positive": {"$sum": "$positive"},
            }
        },
    ]
    if start_date != None and start_date != "":
        # pipeline[0]["$match"]["$and"].append({"date_created": {"$gte": ""}})
        _start_date = datetime.strptime(start_date, "%d/%m/%Y")
        pipeline[0]["$match"]["$and"].append({"date_created": {"$gte": _start_date}})

    if end_date != None and end_date != "":
        # pipeline[0]["$match"]["$and"].append({"date_created": {"$lte": ""}})
        _end_date = datetime.strptime(end_date, "%d/%m/%Y")
        pipeline[0]["$match"]["$and"].append({"date_created": {"$lte": _end_date}})

    data,_ = MongoRepository().aggregate("events", pipeline)

    result = {"nodes": [], "edges": []}
    for object_name in object_names:
        result["nodes"].append(
            {"id": object_name, "img": object_image_dict[object_name]}
        )

    for row in data:
        source = process_source_target(
            row["_id"]["source"], countries_dict, country_regex
        )
        target = process_source_target(
            row["_id"]["target"], countries_dict, country_regex
        )
        target = process_duplicate_source_target(source, target)
        pairs = list(
            filter(
                lambda pair: pair[0] in object_names and pair[1] in object_names,
                create_source_target_pair(source, target),
            )
        )
        if pairs == []:
            continue
        print("sađâsđâs,", list(pairs))

        count_sentiment = (
            int(row["normal"]) + int(row["negative"]) + int(row["positive"])
        )
        for pair in pairs:
            result["edges"].append(
                {
                    "source": pair[0],
                    "target": pair[1],
                    "positive": row["positive"],
                    "normal": row["normal"],
                    "negative": row["negative"],
                    "total": count_sentiment,
                }
            )
    result["edges"] = group_edges_by_pair(result)
    return result


async def get_events_data_by_edge(objects, start_date, end_date):
    result = {}
    query = {
        "$and": [
            {"chu_the": {"$regex": objects["source"]}},
            {"khach_the": {"$regex": objects["target"]}},
        ]
    }
    if start_date != None and start_date != "":
        _start_date = datetime.strptime(start_date, "%d/%m/%Y")
        query["$and"].append({"date_created": {"$gte": _start_date}})

    if end_date != None and end_date != "":
        _end_date = datetime.strptime(end_date, "%d/%m/%Y")
        query["$and"].append({"date_created": {"$lte": _end_date}})
    data, _ = MongoRepository().get_many("events", query)
    for row in data:
        row["_id"] = str(row["_id"])
        row["date_created"] = str(row["date_created"])
        if result.get(row["sentiment"]) == None:
            result[row["sentiment"]] = []

        if "new_list" in row:
            # new_list = find_news_by_filter(
            #     {"_id": {"$in": convert_map_str_to_object_id(row["new_list"])}},
            #     {"_id": 1, "data:title": 1, "data:url": 1},
            # )
            new_list = await client2.find(
                {"_id": {"$in": convert_map_str_to_object_id(row["new_list"])}},
                projection={"_id": 1, "data:title": 1, "data:url": 1},
            ).to_list(None)
            for item in new_list:
                item["_id"] = str(item["_id"])

            row["new_list"] = new_list

        result[row["sentiment"]].append(row)

    return result
