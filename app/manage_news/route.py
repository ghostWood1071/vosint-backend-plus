from typing import List, Optional, Any

from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from app.manage_news.model import SourceGroupSchema
from app.manage_news.service import (
    count_search_source_group,
    count_source,
    count_source_group,
    create_source_group,
    delete_source_group,
    find_by_filter_and_paginate,
    get,
    get_by_user_id,
    search_by_filter_and_paginate,
    update_source_group,
    get_topic_dropdown
)
from db.init_db import get_collection_client
import traceback

router = APIRouter()

db = get_collection_client("Source")

@router.get("/get-topic-dropdown")
def route_get_topic_dropdown(authorize: AuthJWT = Depends())->Any:
    try: 
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        data = get_topic_dropdown(user_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("")
async def create(data: SourceGroupSchema = Body(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    source = data.dict()
    source["user_id"] = user_id
    # exist_source = await db.find_one({"source_name": source["source_name"]})
    # if exist_source:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT, detail="source group already exist"
    #     )
    created_source_group = await create_source_group(source)
    if created_source_group:
        return status.HTTP_201_CREATED
    return status.HTTP_403_FORBIDDEN


# @router.get("")
# async def get_all(skip=1, limit=10):
#     list_source_group = await find_by_filter_and_paginate({}, int(skip), int(limit))
#     count = await count_source({})
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"data": list_source_group, "total_record": count},
#     )


@router.get("")
async def search(
    text_search: Optional[str] = "", skip=1, limit=10, authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    search_source_group = await search_by_filter_and_paginate(
        text_search, user_id, int(skip), int(limit)
    )
    count_source = await count_search_source_group(text_search, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": search_source_group, "total_record": count_source},
    )


@router.get("/get_by_user")
async def get_by_user(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    search_source_group = await get_by_user_id(user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": search_source_group},
    )


@router.put("/{id}")
async def update_all(
    id: str, data: SourceGroupSchema = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    list_source = await get({})

    data = {k: v for k, v in data.dict().items() if v is not None}
    data["user_id"] = user_id
    updated_source_group = await update_source_group(id, data, list_source)
    if updated_source_group:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.delete("/{id}")
async def delete_source(id):
    Deleted_group_source = await delete_source_group(id)
    if Deleted_group_source:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN
