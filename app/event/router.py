import json
from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from app.event.model import AddNewEvent, CreateEvent, UpdateEvent
from app.event.service import (
    add_event,
    add_list_event_id,
    add_list_new,
    add_list_new_id,
    count_chu_khach,
    count_event,
    count_event_system,
    delete_event,
    delete_list_new,
    event_detail,
    event_detail_system,
    get_all_by_paginate,
    get_all_by_system,
    get_by_new_id,
    get_chu_khach,
    get_system_by_new_id,
    remove_list_event_id,
    remove_list_new_id,
    search_chu_khach,
    search_event,
    search_id,
    search_result,
    update_add,
    update_add_system,
    update_event,
    get_events_by_ids,
    get_news_by_ids,
    check_read_events,
    un_check_read_events,
    get_graph_data,
    get_events_data_by_edge,
)
from db.init_db import get_collection_client
from word_exporter import export_events_to_words
from fastapi import Response
from typing import *

router = APIRouter()
client = get_collection_client("event")
client3 = get_collection_client("events")
report_client = get_collection_client("report")

projection = {"_id": True, "data:title": True, "data:url": True}
projection_rp = {"_id": True, "title": True}


@router.get("/all-system-created")
async def get_all(skip=1, limit=10):
    list_event = await get_all_by_system({}, int(skip), int(limit))
    count = await count_event_system({})
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"data": list_event, "total": count}
    )


@router.post("")
async def create_event(data: CreateEvent = Body(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    event = data.dict()
    event["user_id"] = user_id
    event["date_created"] = datetime.strptime(event["date_created"], "%d/%m/%Y")
    if event["system_created"] == True:
        exist_event_system = await client3.find_one({"event_name": event["event_name"]})
        event["user_id"] = 0
        if exist_event_system:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="event already exist"
            )
    if event["system_created"] == False:
        exist_event = await client.find_one({"event_name": event["event_name"]})
        if exist_event:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="event already exist"
            )
    event["total_new"] = len(event["new_list"])
    event_created = await add_event(event)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=str(event_created.inserted_id)
    )


@router.put("/add-new/{id_event}")
async def add_new_list(id_event: str, list_id_new: List[str] = Body(...)):
    list_new = []
    for item in list_id_new:
        list_new.append(ObjectId(item))
    await add_list_new_id(id_event, list_id_new)
    return status.HTTP_201_CREATED


@router.put("/remove-new/{id_event}")
async def remove_new_list(id_event: str, list_id_new: List[str] = Body(...)):
    list_new = []
    for item in list_id_new:
        list_new.append(ObjectId(item))
    await remove_list_new_id(id_event, list_id_new)
    return JSONResponse(status_code=status.HTTP_200_OK, content="Successful remove")


# @router.put("/add-new/")
# async def add_more_new(id_new: str, list_news: List[AddNewEvent] = Body(...)):
#     id_obj = ObjectId(id_new)
#     news = []
#     for list_new in list_news:
#         follow = AddNewEvent(
#             id_new=list_new.id_new, data_title=list_new.data_title, data_url=list_new.data_url
#         )
#         news.append(follow)
#     await add_list_new(id_obj, news)
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content="Successful add")


# @router.put("/remove-new/")
# async def remove_new(id_event: str, list_news: List[AddNewEvent] = Body(...)):
#     id_ev = ObjectId(id_event)
#     list_exist_new = []
#     for item in list_news:
#         list_exist_new.append(item)
#     await delete_list_new(id_ev, list_exist_new)
#     return JSONResponse(status_code=status.HTTP_200_OK, content="Successful remove")


@router.put("/add-event/{id_new}")
async def add_event_list(id_new: str, list_id_event: List[str] = Body(...)):
    list_new = []
    for item in list_id_event:
        list_new.append(ObjectId(item))
    await add_list_event_id(id_new, list_id_event)
    return status.HTTP_201_CREATED


@router.put("/remove-event/{id_new}")
async def remove_event_list(id_new: str, list_id_event: List[str] = Body(...)):
    list_event = []
    for item in list_id_event:
        list_event.append(ObjectId(item))
    await remove_list_event_id(id_new, list_id_event)
    return JSONResponse(status_code=status.HTTP_200_OK, content="Successful remove")


@router.get("")
async def get_all(skip=1, limit=10):
    list_event = await get_all_by_paginate({}, int(skip), int(limit))
    count = await count_event({})
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"data": list_event, "total": count}
    )


@router.get("/detail/{event_id}")
async def get_event(event_id: str):
    detail = await event_detail(event_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="event not exist"
        )
    return detail


@router.get("/detail-system/{event_id}")
async def get_event(event_id: str):
    detail = await event_detail_system(event_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="event not exist"
        )

    return detail


@router.get("/news/{news_id}")
async def show_event_by_news(news_id: str):
    detail = await get_by_new_id(news_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="event not exist"
        )
    return detail


@router.get("/news/system/{news_id}")
async def show_event_by_news_and_system(news_id: str):
    detail = await get_system_by_new_id(news_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="event not exist"
        )
    return detail


@router.get("/search")
async def search_by_name(
    event_name: Optional[str] = "",
    id_new: Optional[str] = "",
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    system_created: Optional[bool] = False,
    skip=1,
    limit=10,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    search_list = await search_event(
        event_name,
        id_new,
        start_date,
        end_date,
        user_id,
        system_created,
        int(skip),
        int(limit),
    )
    count = await search_result(
        event_name, id_new, start_date, end_date, user_id, system_created
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"data": search_list, "total": count}
    )


@router.get("/search-based-user-id")
async def search_based_id_system(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    search_list = await search_id(user_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": search_list})


@router.get("/get-chu-the-khach-the")
async def get_chu_khach_the(
    text_search: Optional[str] = None, skip=1, limit=10, authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    list_c_k = await get_chu_khach(user_id, text_search, int(skip), int(limit))
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": list_c_k})


@router.get("/search-based-chu-the-khach-the")
async def search_base_chu_khach(
    chu_the: Optional[str] = None,
    khach_the: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip=1,
    limit=10,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    list_ev = await search_chu_khach(
        user_id, chu_the, khach_the, start_date, end_date, int(skip), int(limit)
    )
    count = await count_chu_khach(chu_the, khach_the, start_date, end_date, user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": list_ev, "total": count}
    )


@router.put("/clone-event/{id_event}")
async def clone_event(
    id_event: str,
    report_id: str = "",
    heading_id: str = "",
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()

    if report_id == "" and heading_id == "":
        cursor = await client3.find_one({"_id": ObjectId(id_event)})
    else:
        cursor = await client3.find_one(
            {"_id": ObjectId(id_event)}
        ) or await client.find_one({"_id": ObjectId(id_event)})

    if cursor:
        if report_id == "" and heading_id == "":
            existing_cloned = await client.find_one({"_id": ObjectId(id_event)})
            if existing_cloned and "system_created" not in existing_cloned:
                raise HTTPException(status_code=400, detail="Event already cloned")

        if "system_created" not in cursor:
            cursor["event_content"] = json.dumps(
                {
                    "root": {
                        "children": [
                            {
                                "children": [
                                    {
                                        "detail": 0,
                                        "format": 0,
                                        "mode": "normal",
                                        "style": "",
                                        "text": cursor["event_content"],
                                        "type": "text",
                                        "version": 1,
                                    }
                                ],
                                "direction": "ltr",
                                "format": "",
                                "indent": 0,
                                "type": "paragraph",
                                "version": 1,
                            }
                        ],
                        "direction": "ltr",
                        "format": "",
                        "indent": 0,
                        "type": "root",
                        "version": 1,
                    }
                }
            )

        cursor["user_id"] = user_id
        for item in cursor["new_list"]:
            if item == "":
                cursor["new_list"] = []
                break

        if report_id != "" and heading_id != "":
            cursor["_id"] = ObjectId()
            cursor["system_created"] = True
            current_event = await client.insert_one(cursor)

            current_report = await report_client.find_one({"_id": ObjectId(report_id)})
            current_heading = {}
            index = -1

            # print(current_report["headings"])
            for index, heading in enumerate(current_report["headings"]):
                if heading["id"] == heading_id:
                    current_heading = heading
                    index = index
                    break

            for i in range(len(current_heading["eventIds"])):
                if current_heading["eventIds"][i] == id_event:
                    current_heading["eventIds"][i] = str(current_event.inserted_id)
                    break

            report_client.update_one(
                {"_id": ObjectId(report_id)},
                {"$set": {f"headings.{index}": current_heading}},
            )
            return await client.find_one({"_id": ObjectId(current_event.inserted_id)})

        await client.insert_one(cursor)
        await client3.update_one(
            {"_id": ObjectId(id_event)},
            {"$addToSet": {"list_user_clone": user_id}},
        )
        return {"message: Event cloned successfully"}
    else:
        return {"message": "Event not found"}


@router.put("/delete-cloned-event/{id_event}")
async def delete_clone(id_event: str, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    await client.delete_one({"_id": ObjectId(id_event)})
    await client3.update_one(
        {"_id": ObjectId(id_event)},
        {
            "$pull": {"list_user_clone": {"$in": [user_id]}},
        },
    )
    return {"message": "Remove event cloned successfully"}


@router.put("/update-to-add/{id}")
async def update_to_add(
    id: str, data: UpdateEvent = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    created = data.dict()
    created["system_created"] = False
    created["user_id"] = user_id
    await update_add(id, created)
    return 200


@router.put("/update-to-add-event-system/{id}")
async def update_to_add_system(
    id: str, data: UpdateEvent = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    created = data.dict()
    created["system_created"] = False
    created["user_id"] = user_id
    await update_add_system(id, created)
    return 200


@router.put("/{id}")
async def update(
    id: str, data: UpdateEvent = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    data = {k: v for k, v in data.dict().items() if v is not None}
    if data["system_created"] == True:
        data["user_id"] = 0
    if data["system_created"] == False:
        data["user_id"] = user_id
    data["date_created"] = datetime.strptime(data["date_created"], "%d/%m/%Y")
    data["total_new"] = len(data["new_list"])
    updated_event = await update_event(id, data)
    if updated_event:
        return 200
    return status.HTTP_403_FORBIDDEN


@router.delete("/{id}")
async def remove_event(id, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    deleted = await delete_event(id, user_id)
    if deleted:
        return {"messsage": "event deleted successful"}
    return status.HTTP_403_FORBIDDEN


@router.post("/export-to-word")
async def export_event_to_word(event_ids: List[str]):
    events = await get_events_by_ids(event_ids)
    news_ids_spec = []
    for event in events:
        for news_id in event["new_list"]:
            news_ids_spec.append(news_id)
    news = await get_news_by_ids(news_ids_spec)
    for event in events:
        if event.get("source_list") is None:
            event["source_list"] = []
        for source_id in event["new_list"]:
            event["source_list"].append(news[source_id])
    file_buff = export_events_to_words(events)
    nowstr = datetime.now().strftime("%d-%m-%Y")
    return Response(
        file_buff.read(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Content-Disposition": f"attachment; filename=su_kien({nowstr}).docx",
        },
    )


@router.post("/read-check")
def read_events(
    event_ids: List[str], is_system_created: bool = True, authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    result = check_read_events(event_ids, user_id, is_system_created)
    return result


@router.post("/read-uncheck")
def unread_events(
    event_ids: List[str],
    is_system_created: bool = True,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    result = un_check_read_events(event_ids, user_id, is_system_created)
    return result


@router.post("/get-international-graph")
def get_international_graph(
    object_ids: List[str], start_date: str = "", end_date: str = ""
):
    data = get_graph_data(object_ids, start_date, end_date)
    return JSONResponse(data, 200)


@router.post("/get-events-by-edge")
async def get_events_by_edge(
    objects: Dict[str, Any], start_date: str = "", end_date: str = ""
):
    # try:
    #     start_date = (
    #         start_date.split("/")[2]
    #         + "-"
    #         + start_date.split("/")[1]
    #         + "-"
    #         + start_date.split("/")[0]
    #         + "T00:00:00Z"
    #     )
    # except:
    #     pass
    # try:
    #     end_date = (
    #         end_date.split("/")[2]
    #         + "-"
    #         + end_date.split("/")[1]
    #         + "-"
    #         + end_date.split("/")[0]
    #         + "T00:00:00Z"
    #     )
    # except:
    #     pass
    data = await get_events_data_by_edge(objects, start_date, end_date)
    return JSONResponse(data, 200)
