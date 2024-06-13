from datetime import datetime

from pymongo import DESCENDING

from db.init_db import get_collection_client

client = get_collection_client("News_vnanet")


async def get_all(text_search, start, end, check, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    query = {}
    list_craw = []
    if text_search:
        query = {"title": {"$regex": text_search, "$options": "i"}}
    if start and end:
        start_date = datetime.strptime(start, "%d/%m/%Y")
        end_date = datetime.strptime(end, "%d/%m/%Y")
        query = {"date": {"$gte": start_date, "$lte": end_date}}
    if check == "All":
        query = {}
    if check == "crawled":
        query = {"is_crawled": True}
    if check == "not crawl":
        query = {"is_crawled": False}
    if not query:
        query = {}
    async for item in client.find(query).sort("date", DESCENDING).skip(offset).limit(
        limit
    ):
        list_craw.append(item)
    return list_craw


async def count(text_search, start, end, check, skip: int, limit: int):
    query = {}
    conditions = []

    if text_search:
        conditions.append({"title": {"$regex": text_search, "$options": "i"}})
    if start and end:
        start_date = datetime.strptime(start, "%d/%m/%Y")
        end_date = datetime.strptime(end, "%d/%m/%Y")
        conditions.append({"date": {"$gte": start_date, "$lte": end_date}})
    if check == "All":
        conditions.append({})
    if check == "crawled":
        conditions.append({"is_crawled": True})
    if check == "not crawl":
        conditions.append({"is_crawled": False})
    if conditions:
        query["$and"] = conditions
    return await client.count_documents(query)
