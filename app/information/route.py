from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse

from app.information.model import CreateInfor, UpdateInfor
from app.information.service import (
    aggregate_infor,
    count_infor,
    count_search_infor,
    create_infor,
    delete_infor,
    find_by_filter_and_paginate,
    search_by_filter_and_paginate,
    update_infor,
    get_source_dropdown
)
from db.init_db import get_collection_client
from typing import List, Any
import traceback
 
router = APIRouter()
infor_collect = get_collection_client("infor")

@router.get("/get-source-dropdown")
def route_get_source_dropdown()->Any:
    try: 
        data = get_source_dropdown()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
        
@router.post("")
async def add_infor(payload: CreateInfor):
    infor = payload.dict()
    exist_infor = await infor_collect.find_one({"name": infor["name"]})
    if exist_infor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="source already exist"
        )
    new_infor = await create_infor(infor)
    if new_infor:
        return 200
    return status.HTTP_403_FORBIDDEN


@router.get("")
async def get_all(skip=1, limit=10):
    list_infor = await find_by_filter_and_paginate({}, int(skip), int(limit))
    count = await count_infor({})
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": list_infor, "total_record": count},
    )


@router.get("/pipeline-options")
async def get_options_pipeline():
    pipeline = [
        {
            "$addFields": {
                "label": {"$concat": ["$name", " (", "$host_name", ")"]},
                "value": {"$convert": {"input": "$_id", "to": "string"}},
            }
        },
        {"$project": {"value": 1, "label": 1, "_id": 0}},
    ]
    list_info = await aggregate_infor(pipeline)
    return JSONResponse(status_code=status.HTTP_200_OK, content=list_info)


@router.get("/{name}")
async def search(name, skip=1, limit=10):
    list_infor = await search_by_filter_and_paginate(name, int(skip), int(limit))
    count = await count_search_infor(name)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": list_infor, "total_record": count},
    )


@router.put("/{id}")
async def update(id, data: UpdateInfor = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    updated_infor = await update_infor(id, data)
    if updated_infor:
        return status.HTTP_200_OK
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="update unsuccessful"
    )


@router.delete("/{id}")
async def delete(id):
    deleted_infor = await delete_infor(id)
    if deleted_infor:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN

