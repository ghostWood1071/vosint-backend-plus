from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Path, status
from fastapi.responses import JSONResponse

from app.user_config.model import UserConfig
from app.user_config.service import get_all_user, update_user_config
from db.init_db import get_collection_client

client = get_collection_client("user_config")

router = APIRouter()


@router.get("")
async def get_all():
    users = await get_all_user()
    if users:
        return users
    obj = {
        "username": "",
        "password": "",
        "tag": "using",
        "list_proxy": [],
        "cookies": [],
    }
    client.insert_one(obj)
    users = await get_all_user()
    return users


@router.put("/{id}")
async def update(id: str, data: UserConfig = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    await update_user_config(id, data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Successful update",
    )
