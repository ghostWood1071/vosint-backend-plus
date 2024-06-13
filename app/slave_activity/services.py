from typing import List, Optional

from bson import ObjectId
from fastapi import status
import pytz

from db.init_db import get_collection_client
import pymongo
from datetime import datetime, timedelta

slave_activity_client = get_collection_client("slave_activity")


async def crawler_log(page_index=1, page_size=10):
    skip = int(page_size) * (int(page_index) - 1)
    list_slave = await slave_activity_client.aggregate([]).to_list(None)

    result = []
    async for item in slave_activity_client.find({}).skip(skip).limit(page_size):
        result.append(item)
    return {"data": result, "total": len(list_slave)}
