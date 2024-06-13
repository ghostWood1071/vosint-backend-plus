from datetime import datetime, time, timedelta
from typing import List

import pydantic
from bson.objectid import ObjectId

from db.init_db import get_collection_client

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str


report_client = get_collection_client("report")
event_client = get_collection_client("event")
event_system_client = get_collection_client("event_system")
new_client = get_collection_client("News")
newsletter_client = get_collection_client("newsletter")

projection = {
    "_id": True,
    "title": True,
    "parent_id": True,
}

projection_event = {"event_name": True, "new_list": True, "date_created": True}

projection_new = {"_id": True, "data:title": True, "data:url": True, "created_at": True}


async def count(filter):
    return await report_client.count_documents(filter)


async def get_reports(filter, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    list_report = []
    async for report in report_client.find(filter).sort("_id").skip(offset).limit(
        limit
    ):
        list_report.append(report)

    return list_report


async def find_report_by_filter(filter, projection=None):
    list_report = []
    async for report in report_client.find(filter, projection).sort("_id"):
        list_report.append(report)

    return list_report


async def get_report(id: str):
    return await report_client.find_one({"_id": ObjectId(id)})


async def create_report(report):
    created_rp = await report_client.insert_one(report)
    id_rp = str(created_rp.inserted_id)
    eventList = report.get("event_list", [])
    await event_client.update_many(
        {"_id": {"$in": [ObjectId(event_id) for event_id in eventList]}},
        {"$addToSet": {"list_report": id_rp}},
    )
    return created_rp


async def update_report(id: str, report: dict):
    updated_rp = await report_client.update_one({"_id": ObjectId(id)}, {"$set": report})
    return updated_rp


async def delete_report(id: str):
    deleted_rp = await report_client.delete_one({"_id": ObjectId(id)})
    await event_client.update_many(
        {"list_report": id},
        {"$pull": {"list_report": {"$in": [id]}}},
    )
    return deleted_rp


async def get_event(data):
    list_ev = []

    for data_model in data:
        # Find the newsletter document by its id_linh_vuc
        newsletter_doc = await newsletter_client.find_one(
            {"_id": ObjectId(data_model.id_linh_vuc)}, projection
        )

        if newsletter_doc and "events" not in newsletter_doc:
            ll = []
            if data_model.start and data_model.end is not None:
                # Convert start and end dates to datetime objects
                start_date = datetime.strptime(data_model.start, "%d/%m/%Y").date()
                datetime_start = datetime.combine(start_date, datetime.min.time())

                end_date = datetime.strptime(data_model.end, "%d/%m/%Y").date()
                datetime_end = datetime.combine(end_date, datetime.max.time())

                # Query the events collection
                query = {
                    "$and": [
                        {"list_linh_vuc": data_model.id_linh_vuc},
                        {
                            "date_created": {
                                "$gte": datetime_start,
                                "$lte": datetime_end,
                            }
                        },
                    ]
                }

                async for event_doc in event_client.find(query, projection_event):
                    # Convert date_created field to datetime object
                    if "date_created" in event_doc:
                        try:
                            event_doc["date_created"] = str(event_doc["date_created"])
                        except ValueError:
                            pass

                    # Query the news collection and sort by created_at field
                    ll2 = []
                    for new_id in event_doc.get("new_list", []):
                        id_new = {"_id": ObjectId(new_id)}
                        async for new_doc in new_client.find(
                            id_new, projection_new
                        ).sort("created_at", -1).limit(data_model.count):
                            try:
                                new_doc["created_at"] = datetime.strptime(
                                    new_doc["created_at"], "%Y/%m/%d %H:%M:%S"
                                )
                            except ValueError:
                                pass
                            ll2.append(new_doc)

                    # Sort the news list by created_at field and limit to data_model.count
                    ll2 = sorted(ll2, key=lambda x: x.get("created_at"), reverse=True)[
                        : data_model.count
                    ]

                    event_doc["new_list"] = ll2
                    ll.append(event_doc)
            else:
                # Query the events collection
                query = {
                    "$or": [
                        {"list_linh_vuc": data_model.id_linh_vuc},
                    ]
                }

                async for event_doc in event_client.find(query, projection_event):
                    # Convert date_created field to datetime object
                    if "date_created" in event_doc:
                        try:
                            event_doc["date_created"] = str(event_doc["date_created"])
                        except ValueError:
                            pass

                    # Query the news collection and sort by created_at field
                    ll2 = []
                    for new_id in event_doc.get("new_list", []):
                        id_new = {"_id": ObjectId(new_id)}
                        async for new_doc in new_client.find(
                            id_new, projection_new
                        ).sort("created_at", -1).limit(data_model.count):
                            try:
                                new_doc["created_at"] = datetime.strptime(
                                    new_doc["created_at"], "%Y/%m/%d %H:%M:%S"
                                )
                            except ValueError:
                                pass
                            ll2.append(new_doc)

                    # Sort the news list by created_at field and limit to data_model.count
                    ll2 = sorted(ll2, key=lambda x: x.get("created_at"), reverse=True)[
                        : data_model.count
                    ]

                    event_doc["new_list"] = ll2
                    ll.append(event_doc)

            newsletter_doc["events"] = ll

        list_ev.append(newsletter_doc)

    return list_ev


async def remove_report(id_rp: str):
    await report_client.delete_one({"_id": ObjectId(id_rp)})
    await event_client.update_many(
        {"list_report": id_rp},
        {"$pull": {"list_report": {"$in": [id_rp]}}},
    )


async def remove_heading_of_report(id_rp, id_heading: str):
    report = await report_client.find_one({"_id": ObjectId(id_rp)})
    headings = report["headings"]
    for item in headings:
        if id_heading == item["id"]:
            await report_client.update_one(
                {"_id": ObjectId(id_rp)}, {"$pull": {"headings": {"id": id_heading}}}
            )
        for id_ev in item["eventIds"]:
            await event_client.update_many(
                {"_id": ObjectId(id_ev)},
                {"$pull": {"list_report": {"$in": [id_rp]}}},
            )


async def add_heading_of_report(id_rp, id_heading: str, list_id_event: List[ObjectId]):
    report = await report_client.find_one({"_id": ObjectId(id_rp)})
    headings = report["headings"]
    for item in headings:
        if id_heading == item["id"]:
            await report_client.update_many(
                {"_id": ObjectId(id_rp)},
                {
                    "$addToSet": {
                        "headings.$[elem].eventIds": {
                            "$each": [ObjectId(event_id) for event_id in list_id_event]
                        }
                    }
                },
                array_filters=[{"elem.id": id_heading}],
            )
        for id_ev in item["eventIds"]:
            await event_client.update_many(
                {"_id": ObjectId(id_ev)},
                {"$addToSet": {"list_report": id_rp}},
            )
