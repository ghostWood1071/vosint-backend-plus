from typing import List, Optional, Union, Any
from bson import ObjectId
from fastapi import APIRouter, Body, File, HTTPException, Path, UploadFile, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from app.auth.password import get_password_hash, verify_password_hash
from app.news.services import count_news, find_news_by_filter_and_paginate
from app.social_media.services import find_object_by_filter
from db.init_db import get_collection_client

from .models import InterestedModel, Role, UserCreateModel, UserUpdateModel, BaseUser, User
from .services import *
from bson.json_util import dumps

router = APIRouter()
"""
    Required Authorization
"""

projection = {
    "data:title": True,
    "data:html": True,
    "data:author": True,
    "data:time": True,
    "data:content": True,
    "data:url": True,
    "data:class": True,
    "data:class_sacthai": True,
    "created_at": True,
    "modified_at": True,
    "keywords": True,
    "pub_date": True,
}
client = get_collection_client("users")


@router.post("")
async def add(body: UserCreateModel):
    user_dict = body.dict()

    existing_user = await client.find_one({"username": user_dict["username"]})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tên tài khoản đã tồn tại. Vui lòng nhập lại",
        )

    user_dict["hashed_password"] = get_password_hash(user_dict["password"])
    user_dict.pop("password")
    await create_user(user_dict)
    return HTTPException(status_code=status.HTTP_200_OK)


@router.get("/me")
async def get_me(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))
    if user is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=None)

    return JSONResponse(status_code=status.HTTP_200_OK, content=user_entity(user))


@router.get("/vital")
async def get_vital_by_user(skip=1, limit=20, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": [], "total_record": 0}
        )

    if "vital_list" not in user:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": [], "total_record": 0}
        )

    news = await find_news_by_filter_and_paginate(
        {"_id": {"$in": user["vital_list"]}}, projection, int(skip), int(limit)
    )

    count = await count_news({"_id": {"$in": user["vital_list"]}})

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": news, "total_record": count}
    )


@router.get("/bookmarks")
async def get_news_bookmarks(skip=1, limit=20, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": [], "total_record": 0}
        )

    if "news_bookmarks" not in user:
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": [], "total_record": 0}
        )

    news = await find_news_by_filter_and_paginate(
        {"_id": {"$in": user["news_bookmarks"]}}, projection, int(skip), int(limit)
    )

    count = await count_news({"_id": {"$in": user["news_bookmarks"]}})

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": news, "total_record": count}
    )


@router.get("/interested/{social_type}")
async def get_interested(
    social_type: Optional[str] = Path(
        ...,
        title="Social Type",
        enum=["Object", "Group", "Fanpage"],
    ),
    social_name: str = "",
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))

    if user is None:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": []})

    if "interested_list" not in user:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": []})

    filter = {"_id": {"$in": user["interested_list"]}}
    if social_type:
        filter["social_type"] = social_type
    if social_name:
        filter["social_name"] = {"$regex": f"{social_name.lower()}", "$options": "i"}

    objects = await find_object_by_filter(filter)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": objects})


@router.post("/bookmarks")
async def add_news_to_bookmarks(
    bookmarks: List[str] = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    id_obj = ObjectId(authorize.get_jwt_subject())
    list_bookmark_news = []
    for bookmark in bookmarks:
        list_bookmark_news.append(ObjectId(bookmark))
    await update_bookmark_user(id_obj, list_bookmark_news)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=None)


@router.put("/bookmarks")
async def delete_news_in_bookmarks(
    id_bookmarks: List[str] = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    id_obj = ObjectId(authorize.get_jwt_subject())
    list_bookmark_news = []
    for id_bookmark in id_bookmarks:
        list_bookmark_news.append(ObjectId(id_bookmark))
    await delete_bookmark_user(id_obj, list_bookmark_news)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=None)


@router.post("/vital")
async def add_vital(vitals: List[str] = Body(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    list_vitals_news = []
    for vital in vitals:
        list_vitals_news.append(ObjectId(vital))
    await update_vital_user(user_id, list_vitals_news)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content="Successful add vital news"
    )


@router.put("/vital")
async def delete_vital(
    id_vitals: List[str] = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    list_vitals_news = []
    for id_vital in id_vitals:
        list_vitals_news.append(ObjectId(id_vital))
    await delete_vital_user(user_id, list_vitals_news)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content="Successful delete vital news"
    )


@router.post("/interested")
async def add_interested(
    interested: InterestedModel = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())
    interested_list = [ObjectId(interested.id)]
    exist_id = await client.find_one(
        {"_id": user_id, "interested_list": {"$in": [ObjectId(interested.id)]}}
    )
    if exist_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The interested object already in database",
        )
    await update_interested_object(user_id, interested_list)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content="Successful add interested object"
    )


@router.delete("/interested/{item_id}")
async def delete_interested_item(
    item_id: str,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": "User not found"}
        )
    await delete_item_from_interested_list(user_id, [ObjectId(item_id)])
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED, content="Successful delete"
    )


@router.get("")
async def get_all(
    skip=1,
    limit=20,
    name="",
    role: Union[Role, None] = None,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()

    query = {
        "$or": [
            {"full_name": {"$regex": f"\\b{name}\\b", "$options": "i"}},
            {"full_name": {"$regex": name, "$options": "i"}},
            {"username": {"$regex": f"\\b{name}\\b", "$options": "i"}},
            {"username": {"$regex": name, "$options": "i"}},
        ]
    }

    if role is not None:
        query["$and"] = [{"role": role}]

    users = await get_users(query, int(skip), int(limit))
    count = await count_users(query)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": users, "total_record": count}
    )


@router.put("/me")
async def update_me(
    user_data: UserUpdateModel = Body(...), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())

    user_data = {k: v for k, v in user_data.dict().items() if v is not None}
    updated_user = await update_user(user_id, user_data)
    if updated_user is None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=None)

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=None)


@router.put("/profile")
async def update_me(user_data: UserUpdateModel, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())

    user_data = {k: v for k, v in user_data.dict().items() if v is not None}
    updated_user = update_user(user_id, user_data)
    if updated_user is None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=None)

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=None)


@router.put("/{id}")
async def update(id: str, body: UserUpdateModel = Body(...)):
    body_dict = {k: v for k, v in body.dict().items() if v is not None}
    user = await find_user_by_id(ObjectId(id))

    a = []
    async for item in client.find():
        if user["_id"] != item["_id"]:
            a.append(item)

    for item in a:
        if body_dict["username"] == item["username"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không được trùng username",
            )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Không tìm thấy nguời dùng"
        )

    if body_dict.get("password"):
        verify_password = verify_password_hash(
            body_dict["password"],
            user["hashed_password"],
        )

        if verify_password == True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới không được trùng với mật khẩu cũ",
            )

        body_dict["hashed_password"] = get_password_hash(body_dict["password"])
        del body_dict["password"]

    updated_user = await update_user(ObjectId(id), body_dict)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=None)

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=None)


@router.delete("/{id}")
async def delete(id: str):
    deleted = await delete_user(id)
    if deleted is not True:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=None)
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=None)


@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = ObjectId(authorize.get_jwt_subject())

    try:
        content = await file.read()
        with open(f"static/{file.filename}", "wb") as f:
            f.write(content)
    except Exception as error:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There was an error when uploading the file",
        )
    finally:
        await file.close()

    update_user(user_id, {"avatar_url": f"static/{file.filename}"})
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED, content=f"static/{file.filename}"
    )

########################### PLUS #################################
@router.get("/get-users")
def route_get_users(
    search_text:str="", page_size:int=10, page_index:int=1,
    branch_id: str="", department_id: str="", role_id: str=""
)->Any:
    try: 
        data = get_users(search_text, page_size, page_index, branch_id, department_id, role_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-user-by-id")
def route_get_user_by_id(user_id:str)->User:
    try: 
        data = get_user(user_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/insert-user")
def route_insert_user(user: User)->str:
    try: 
        data = insert_user(user.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/update-user")
def route_update_user(user: User)->int:
    try: 
        data = update_user(user.user_id, user.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/delete-user")
def route_delete_user(user_ids:list[str])->int:
    try: 
        data = delete_users(user_ids)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-me")
async def route_get_me(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))
    if user is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=None)

    role_collection = get_collection_client("role")
    # role = await role_collection.find_one({"_id": ObjectId(user["role_id"])})
    role = await role_collection.find_one({
        "$or": [
            {"_id": ObjectId(user.get("role_id"))},
            {"role_code": user.get("role")}
        ]
    })

    user["_id"] = str(user["_id"])
    user["role"] = role["role_code"]

    if "role_id" not in user:
        user["role_id"] = str(role["_id"])


    return JSONResponse(status_code=status.HTTP_200_OK, content=user)