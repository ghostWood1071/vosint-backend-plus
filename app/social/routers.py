from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Path, status, UploadFile, File
from fastapi.responses import JSONResponse

from app.social.models import AddFollow, UpdateAccountMonitor, UserCreateModel
from app.social.services import (
    count_object,
    create_user,
    delete_follow_user,
    delete_user,
    get_account_monitor_by_media,
    get_all_user,
    get_user,
    update_account_monitor,
    update_follow_user,
    update_username_user,
    handle_news_files
)
from db.init_db import get_collection_client

client = get_collection_client("socials")

router = APIRouter()


@router.get("")
async def Get_all_user(skip: Optional[int] = None, limit: Optional[int] = None):
    users = await get_all_user(skip, limit)
    if users:
        return users
    return []


@router.get("/{id}")
async def get_user_id(id):
    user = await get_user(id)
    if user:
        return user
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user not exist")


@router.get("/get_by_social/{social}")
async def get_account_monitor_by_medias(
    social: str = Path(
        "Media", title="Social Media", enum=["Facebook", "Twitter", "Tiktok"]
    ),
    username: str = "",
    page: int = 1,
    limit: int = 20,
):
    if social not in ["Facebook", "Twitter", "Tiktok"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid social media"
        )
    filter_object = {"social": social}
    if username:
        filter_object["username"] = {"$regex": f"{username}", "$options": "i"}

    socials = await get_account_monitor_by_media(filter_object, page, limit)

    count = await count_object(filter_object)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": socials, "total_record": count},
    )


@router.post("")
async def add_user(body: UserCreateModel):
    user_dict = body.dict()
    existing_user = await client.find_one({"username": user_dict["username"]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exist"
        )
    await create_user(user_dict)
    return HTTPException(status_code=status.HTTP_200_OK)


@router.delete("/delete/{id}")
async def Delete_user(id: str):
    deleted_user = await delete_user(id)
    if deleted_user:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.put("/update_username")
async def Update_username_user(id_user: str, username_new: str):
    id_obj = ObjectId(id_user)
    await update_username_user(id_obj, username_new)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=None)


@router.put("/add_follow")
async def Update_follow_user(id_user: str, list_follows: List[AddFollow] = Body(...)):
    id_obj = ObjectId(id_user)
    follows = []
    for list_follow in list_follows:
        follow = AddFollow(
            follow_id=list_follow.follow_id, social_name=list_follow.social_name
        )
        follows.append(follow)
    await update_follow_user(id_obj, follows)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content="Successful edit")


@router.put("/delete_follow")
async def Delete_follow_user(
    id_user: str, id_users_follow: List[AddFollow] = Body(...)
):
    id_obj = ObjectId(id_user)
    list_id_new = []
    for id_user in id_users_follow:
        list_id_new.append(id_user)
    await delete_follow_user(id_obj, list_id_new)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content="Successful delete"
    )


@router.put("/edit_account_monitor")
async def update_social(data: UpdateAccountMonitor = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    updated_social = await update_account_monitor(data)
    if updated_social:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Successful edit",
        )
    return status.HTTP_403_FORBIDDEN


@router.post("/upload-news")
async def upload_news(file: UploadFile = File(...)):
    data = await file.read()
    result = await handle_news_files(data)
    return result