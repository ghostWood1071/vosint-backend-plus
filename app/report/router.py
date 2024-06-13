from typing import Annotated, List, Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Body, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
import re

from db.init_db import get_collection_client

from .model import CreateQuickReport, CreateReport, GetEvents, UpdateReport
from .service import (
    add_heading_of_report,
    count,
    create_report,
    delete_report,
    get_event,
    get_report,
    get_reports,
    remove_heading_of_report,
    remove_report,
    update_report,
)

event_client = get_collection_client("event")

router = APIRouter()


@router.get("/quick-report")
async def read_reports_quick(
    title: str = "", skip: int = 0, limit: int = 10, auth: AuthJWT = Depends()
):
    auth.jwt_required()

    # get all report with empty user_id
    query = {
        "$or": [
            {"title": {"$regex": title, "$options": "i"}},
        ],
        "user_id": {"$exists": False},
    }

    reports = await get_reports(query, skip, limit)
    reports_count = await count(query)
    return {
        "data": reports,
        "total": reports_count,
    }


@router.get("")
async def read_reports(
    title: str = "", skip: int = 0, limit: int = 10, auth: AuthJWT = Depends()
):
    auth.jwt_required()
    user_id = auth.get_jwt_subject()

    query = {
        # "$text": {"$search": title},
        "user_id": user_id,
    }
    if title != "":
        query["$text"] = {"$search": title}

    reports = await get_reports(query, skip, limit)
    reports_count = await count(query)

    return {
        "data": reports,
        "total": reports_count,
    }


@router.get("/{id}")
async def read_report(id: str):
    report = await get_report(id)
    return report


@router.post("/quick-report")
async def post_quick_report(
    report: CreateQuickReport = Body(...), auth: AuthJWT = Depends()
):
    try:
        auth.jwt_required()
        pattern = r'[!@#$%^&*+{}\[\]:;<>,.?~\\|"]'
        if re.search(pattern, report.title) or report.title.strip() == "":
            raise Exception("Tiêu đề không chứa ký tự đặc biệt")
        report_dict = report.dict()
        print(report_dict)
        report_created = await create_report(report_dict)
        return report_created.inserted_id
    except Exception as e:
        return JSONResponse(str(e), 500)


@router.post("")
async def post_report(report: CreateReport = Body(...), auth: AuthJWT = Depends()):
    auth.jwt_required()
    user_id = auth.get_jwt_subject()

    report_dict = report.dict()
    report_dict["user_id"] = user_id
    report_created = await create_report(report_dict)
    return report_created.inserted_id


@router.put("/{id}")
async def put_report(id: str, data: UpdateReport = Body(...)):
    event_list = data.event_list
    del data.event_list
    eventList = event_list
    # await event_client.update_many(
    #     {"list_report": id},
    #     {"$pull": {"list_report": {"$in": [id]}}},
    # )
    for ev in eventList:
        ev_id = ev
        await event_client.update_many(
            {"_id": ObjectId(ev_id)}, {"$addToSet": {"list_report": id}}
        )
    # insert id report to event item
    report_dict = {k: v for k, v in data.dict().items() if v is not None}
    await update_report(id, report_dict)
    return id


@router.put("/add-events-to-heading")
async def add_head(
    id_report: Optional[str] = "",
    id_heading: Optional[str] = "",
    list_id_event: List[str] = Body(...),
):
    list_new = []
    for item in list_id_event:
        list_new.append(ObjectId(item))
    await add_heading_of_report(id_report, id_heading, list_id_event)
    return 200


@router.put("/remove-heading/")
async def delete_heading(id_report: Optional[str] = "", id_heading: Optional[str] = ""):
    if id_report and not id_heading:
        await remove_report(id_report)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content="Successful delete a report"
        )
    elif id_report and id_heading:
        await remove_heading_of_report(id_report, id_heading)
        return 200


@router.delete("/{id}")
async def delete(id: str):
    await delete_report(id)
    return id


@router.post("/get-event-with-new/")
async def get_event_route(id_count: List[GetEvents]):
    list_ev = []
    for item in id_count:
        list_ev.append(item)
    reports = await get_event(list_ev)
    return reports
