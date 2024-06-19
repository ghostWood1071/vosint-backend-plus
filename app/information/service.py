from typing import List, Any

from bson.objectid import ObjectId
from fastapi import HTTPException, status

from db.init_db import get_collection_client
from vosint_ingestion.models import MongoRepository

infor_collect = get_collection_client("info")


async def create_infor(infor):
    return await infor_collect.insert_one(infor)


async def aggregate_infor(pipeline):
    items = []
    async for item in infor_collect.aggregate(pipeline):
        items.append(item)

    return items


async def get_all_infor():
    list_infor = []
    async for item in infor_collect.find():
        list_infor.append(entity(item))
    return list_infor


async def find_by_filter_and_paginate(filter, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_infor = []
    async for item in infor_collect.find(filter).sort("_id").skip(offset).limit(limit):
        item = infor_to_json(item)
        list_infor.append(item)
    return list_infor


def infor_to_json(infor) -> dict:
    infor["_id"] = str(infor["_id"])
    return infor


async def count_infor(filter):
    return await infor_collect.count_documents(filter)


async def search_by_filter_and_paginate(name, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_infor = []
    async for item in infor_collect.find(
        {
            "$or": [
                {"name": {"$regex": name, "$options": "i"}},
                {"host_name": {"$regex": name, "$options": "i"}},
            ]
        }
    ).sort("_id").skip(offset).limit(limit):
        item = infor_json(item)
        list_infor.append(item)
    return list_infor


def infor_json(infor) -> dict:
    infor["_id"] = str(infor["_id"])
    return infor


async def count_search_infor(name: str):
    name_filter = {"name": {"$regex": name, "$options": "i"}}
    return await infor_collect.count_documents(name_filter)


async def search_infor(keyword: str) -> dict:
    list_infor = []
    async for item in infor_collect.find(
        {"$or": [{"name": {"$regex": keyword}}, {"host_name": {"$regex": keyword}}]}
    ):
        list_infor.append(entity(item))
    return list_infor


async def update_infor(id: str, data: dict):
    infor = await infor_collect.find_one({"_id": ObjectId(id)})

    list_infor = await infor_collect.find().to_list(length=None)

    for item in list_infor:
        if item["_id"] != infor["_id"] and item["name"] == data["name"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Source is duplicated"
            )

    # if infor["name"] == data["name"]:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Object already exist")

    updated_infor = await infor_collect.find_one_and_update(
        {"_id": ObjectId(id)}, {"$set": data}
    )
    if updated_infor:
        return status.HTTP_200_OK
    else:
        return False


async def delete_infor(id: str):
    infor = await infor_collect.find_one({"_id": ObjectId(id)})
    if infor:
        await infor_collect.delete_one({"_id": ObjectId(id)})
        return True


def entity(infor) -> dict:
    return {
        "_id": str(infor["_id"]),
        "name": infor["name"],
        "host_name": infor["host_name"],
        "language": infor["language"],
        "publishing_country": infor["publishing_country"],
        "source_type": infor["source_type"],
    }

def get_source_dropdown()->Any:
    try:
        result, _ = MongoRepository().find("info", filter_spec={})
        print("result", result)

        return [{"label": item["name"], "value": item["_id"]} for item in result]
    except Exception as e:
        traceback.print_exc()
        raise e