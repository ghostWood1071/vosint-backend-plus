from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Path, status
from fastapi.responses import JSONResponse

from app.slave_activity.models import SlaveActivity

from app.slave_activity.services import (
    crawler_log,
)
from app.slave_activity import services

router = APIRouter()


@router.get("/get-crawler-log")
async def get_crawler_log(page_index=1, page_size=10):
    return await crawler_log(int(page_index), int(page_size))
