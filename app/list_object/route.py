from typing import Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)

my_es = My_ElasticSearch()
from app.list_object.model import CreateObject, UpdateObject
from app.list_object.service import (
    count_all_object,
    count_object,
    count_search_object,
    create_object,
    delete_object,
    find_by_filter_and_paginate,
    find_by_id,
    get_all_object,
    search_by_filter_and_paginate,
    update_object,
    update_news,
)
from app.news.services import (
    count_news,
    find_news_by_filter,
    find_news_by_filter_and_paginate,
)
from db.init_db import get_collection_client
from vosint_ingestion.models import MongoRepository

router = APIRouter()

projection = {
    "data:title": True,
    "data:html": True,
    "data:author": True,
    "data:time": True,
    "data:content": True,
    "data:url": True,
    "data:class": True,
    "data:class_sacthai": True,
    "created_at": True,
    "modified_at": True,
}

db = get_collection_client("object")


@router.post("")
async def add_object(
    payload: CreateObject,
    type: Optional[str] = Query("Type", enum=["Đối tượng", "Tổ chức", "Quốc gia"]),
    Status: Optional[str] = Query("Status", enum=["enable", "disable"]),
):
    Object = payload.dict()
    exist_object = await db.find_one({"name": Object["name"]})
    if exist_object:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="object already exist"
        )

    Object["object_type"] = type
    Object["status"] = Status
    Object["news_list"] = []

    new_object = await create_object(Object)
    if new_object:
        return 200
    return status.HTTP_403_FORBIDDEN


@router.get("/{object_type}")
async def get_type_and_name(
    name: str = "",
    object_type: Optional[str] = Path(
        ..., title="Object type", enum=["Đối tượng", "Tổ chức", "Quốc gia"]
    ),
    skip=1,
    limit=10,
):
    list_obj = await find_by_filter_and_paginate(
        name, object_type, int(skip), int(limit)
    )
    count = await count_object(object_type, name)
    return {"data": list_obj, "total": count}


@router.get("/{id}/news")
async def get_news_by_object_id(
    id: str, skip=1, limit=20, authorize: AuthJWT = Depends()
):
    # authorize.jwt_required()
    # # pipeline = [
    # #     {"$match": {"_id": ObjectId(id)}},
    # #     {
    # #         "$addFields": {
    # #             "news_id": {
    # #                 "$map": {
    # #                     "input": "$news_id",
    # #                     "as": "id",
    # #                     "in": {"$toString": "$$id"},
    # #                 }
    # #             }
    # #         }
    # #     },
    # #     {"$project": {"news_id": 1}},
    # # ]
    # # object = await aggregate_object(pipeline)
    # one_object = await find_by_id(ObjectId(id), {"news_id": 1})
    # if "news_id" not in one_object:
    #     return JSONResponse(
    #         status_code=status.HTTP_200_OK, content={"result": [], "total_record": 0}
    #     )

    # news = await find_news_by_filter_and_paginate(
    #     {"_id": {"$in": one_object["news_id"]}}, projection, int(skip), int(limit)
    # )
    # count = await count_news({"_id": {"$in": one_object["news_id"]}})
    list_id = None
    query = None
    a = MongoRepository().get_one(collection_name="object", filter_spec={"_id": id})
    first_lang = 1
    query = ""
    ### vi
    query_vi = ""
    first_flat = 1
    try:
        for i in a["keyword_vi"]["required_keyword"]:
            if first_flat == 1:
                first_flat = 0
                query_vi += "("
            else:
                query_vi += "| ("
            j = i.split(",")

            for k in j:
                query_vi += "+" + '"' + k + '"'
            query_vi += ")"
    except:
        pass
    try:
        j = a["keyword_vi"]["exclusion_keyword"].split(",")
        for k in j:
            query_vi += "-" + '"' + k + '"'
    except:
        pass

    ### cn
    query_cn = ""
    first_flat = 1
    try:
        for i in a["keyword_vn"]["required_keyword"]:
            if first_flat == 1:
                first_flat = 0
                query_cn += "("
            else:
                query_cn += "| ("
            j = i.split(",")

            for k in j:
                query_cn += "+" + '"' + k + '"'
            query_cn += ")"
    except:
        pass
    try:
        j = a["keyword_cn"]["exclusion_keyword"].split(",")
        for k in j:
            query_cn += "-" + '"' + k + '"'
    except:
        pass

    ### cn
    query_ru = ""
    first_flat = 1
    try:
        for i in a["keyword_ru"]["required_keyword"]:
            if first_flat == 1:
                first_flat = 0
                query_ru += "("
            else:
                query_ru += "| ("
            j = i.split(",")

            for k in j:
                query_ru += "+" + '"' + k + '"'
            query_ru += ")"
    except:
        pass
    try:
        j = a["keyword_ru"]["exclusion_keyword"].split(",")
        for k in j:
            query_ru += "-" + '"' + k + '"'
    except:
        pass

    ### cn
    query_en = ""
    first_flat = 1
    try:
        for i in a["keyword_en"]["required_keyword"]:
            if first_flat == 1:
                first_flat = 0
                query_en += "("
            else:
                query_en += "| ("
            j = i.split(",")

            for k in j:
                query_en += "+" + '"' + k + '"'
            query_en += ")"
    except:
        pass
    try:
        j = a["keyword_en"]["exclusion_keyword"].split(",")
        for k in j:
            query_en += "-" + '"' + k + '"'
    except:
        pass

    if query_vi != "":
        if first_lang == 1:
            first_lang = 0
            query += "(" + query_vi + ")"
    if query_en != "":
        if first_lang == 1:
            first_lang = 0
            query += "(" + query_en + ")"
        else:
            query += "| (" + query_en + ")"
    if query_ru != "":
        if first_lang == 1:
            first_lang = 0
            query += "(" + query_ru + ")"
        else:
            query += "| (" + query_ru + ")"
    if query_cn != "":
        if first_lang == 1:
            first_lang = 0
            query += "(" + query_cn + ")"
        else:
            query += "| (" + query_cn + ")"

    # if text_search != None and news_letter_id != None:
    #     query += '+(' + text_search + ')'
    # elif text_search != None:
    #     query = ''
    #     query += '+(' + text_search + ')'
    query = query

    pipeline_dtos = my_es.search_main(index_name="vosint", query=query)

    for i in range(len(pipeline_dtos)):
        try:
            pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"]["id"]
        except:
            pass
        pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()
    news = pipeline_dtos
    count = len(pipeline_dtos)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": news, "total_record": count}
    )


@router.put("/{id}")
async def update_one(id, data: UpdateObject = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    a = {}

    updated_object = await update_object(id, data)
    update_news(id)
    if updated_object:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.post("/update-news")
def update_news2(object_id: str):
    try:
        object = MongoRepository().get_one("object", {"_id": object_id})
        if object is None:
            return JSONResponse({"success": "false"})
        key_str = ""
        for key in object.get("keywords").keys():
            key_str += object.get("keywords").get(key) + ","
        key_arr = [key.strip() for key in key_str.split(",")]
        key_arr = list(filter(lambda x: x != "", key_arr))
        search_text = " | ".join(key_arr)
        data = my_es.search_main("vosint", query=search_text, size=1000)
        insert_list = [row.get("_id") for row in data]
        # MongoRepository().update_many(
        #     "object",
        #     {"_id": ObjectId(object_id)},
        #     {"$addToSet": {"news_list": {"$each": insert_list}}},
        # )
        return JSONResponse({"success": "true"})
    except Exception as e:
        print(e)
        return JSONResponse({"success": "false"})
    return data


@router.delete("/{id}")
async def delete_one(id):
    deleted_object = await delete_object(id)
    if deleted_object:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN
