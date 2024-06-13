from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from app.user.services import find_user_by_id
from db.init_db import get_collection_client

from .models import (
    AddFollowed,
    CreateSocialModel,
    CreatePriorityModel,
    UpdatePriorityModel,
    UpdateSocial,
    UpdateStatus,
)
from .services import (
    count_object,
    create_social_media,
    delete_followed_by,
    delete_user_by_id,
    find_object_by_filter,
    find_object_by_filter_and_paginate,
    update_followed_by,
    update_social_account,
    update_status_account,
    check_read_socials,
    check_unread_socials,
    feature_keywords,
    get_news_social,
    social_personal,
    statistic_interaction,
    active_member,
    posts_from_priority,
    statistic_interaction_from_priority,
    total_interaction_priority,
    total_post_priority,
    active_member_priority,
    statistic_sentiment,
    post_detail,
    exec_posts,
    exec_create_priority,
    exec_update_priority,
    exec_get_priorities,
    exec_delete_priority,
    exec_influencer,
    exec_influencer_priority,
    exec_influential_post,
)
from word_exporter import export_social_word
from datetime import datetime

client = get_collection_client("social_media")
client2 = get_collection_client("users")

router = APIRouter()


@router.get("/get-priorities")
async def get_priorities(text_search: str = ""):
    return await exec_get_priorities(text_search)


# post
@router.get("/get-posts")
async def get_posts(
    collection_name,
    order=None,
    page_number=None,
    page_size=None,
    text_search="",
    start_date="",
    end_date="",
    sac_thai="",
):
    return await exec_posts(
        collection_name,
        order,
        page_number,
        page_size,
        text_search,
        start_date,
        end_date,
        sac_thai,
    )


# social
@router.get("/get-social-personal")
async def get_social_personal(id: str):
    return await social_personal(id)


@router.get("/get-feature-keywords")
async def get_feature_keywords(
    k: int = 10, start_date: str = "", end_date: str = "", name: str = "facebook"
):
    return await feature_keywords(k, start_date, end_date, name)


@router.get("/get-statistic-interaction")
async def get_statistic_interaction(
    name: str = "", start_date: str = "", end_date: str = ""
):
    return await statistic_interaction(name, start_date, end_date)


@router.get("/get-active-member")
async def get_active_member(name: str = "facebook"):
    return await active_member(name)


@router.get("/get-influencer")
async def get_influencer(
    name: str = "facebook", start_date: str = "", end_date: str = ""
):
    return await exec_influencer(name, start_date, end_date)


@router.get("/get-influencer-priority")
async def get_influencer_priority(name: str = "facebook"):
    return await exec_influencer_priority(name)


@router.get("/get-influential-post")
async def get_influential_post(
    name: str = "facebook", start_date: str = "", end_date: str = ""
):
    return await exec_influential_post(name, start_date, end_date)


# priority
@router.get("/get-posts-from-priority")
async def get_posts_from_priority(
    id_social,
    text_search="",
    page_number=None,
    page_size=None,
    start_date: str = "",
    end_date: str = "",
    sac_thai: str = "",
):
    return await posts_from_priority(
        id_social,
        text_search,
        page_number,
        page_size,
        start_date,
        end_date,
        sac_thai,
    )


@router.get("/get-statistic-interaction-from-priority")
async def get_statistic_interaction_from_priority(
    id_social: str, start_date: str = "", end_date: str = ""
):
    return await statistic_interaction_from_priority(id_social, start_date, end_date)


@router.get("/get-total-interaction-priority")
async def get_total_interaction_priority(
    id_social: str, start_date: str = "", end_date: str = ""
):
    return await total_interaction_priority(id_social, start_date, end_date)


@router.get("/get_total_post_priority")
async def get_total_post_priority(
    id_social: str, start_date: str = "", end_date: str = ""
):
    return await total_post_priority(id_social, start_date, end_date)


@router.get("/get-active-member-priority")
async def get_active_member_priority():
    return await active_member_priority()


# statistic
@router.get("/get-statistic-sentiment")
async def get_statistic_sentiment(
    name: str = "facebook", start_date: str = "", end_date: str = ""
):
    return await statistic_sentiment(name, start_date, end_date)


@router.post("/create-priority")
async def create_priority(body: CreatePriorityModel):
    data_dict = body.dict()
    return await exec_create_priority(data_dict)


@router.post("")
async def add_social(
    body: CreateSocialModel,
):
    social_dict = body.dict()
    existing_user = await client.find_one(
        {
            "$and": [
                {"account_link": social_dict["account_link"]},
                {"social_media": social_dict["social_media"]},
                {"social_type": social_dict["social_type"]},
            ]
        }
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exist"
        )
    await create_social_media(social_dict)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Social media account created successfully."},
        # content={"result": str(result)},
    )


@router.get("/social_media/{social_media}/{social_type}")
async def get_social_by_medias(
    social_media: str = Path(
        "Media", title="Social Media", enum=["Facebook", "Twitter", "Tiktok"]
    ),
    social_type: str = Path(
        "Type", title="Social Type", enum=["Object", "Group", "Fanpage", "All"]
    ),
    social_name: str = "",
    page: int = 0,
    limit: int = 10,
):
    invalid_combinations = {
        "Twitter": ["Group", "Fanpage"],
        "Tiktok": ["Group", "Fanpage"],
    }
    filter_object = {"social_media": social_media}
    if social_type != "All":
        filter_object["social_type"] = social_type
    if social_name:
        filter_object["social_name"] = {"$regex": f"{social_name}", "$options": "i"}
    if (
        social_media in invalid_combinations
        and social_type in invalid_combinations[social_media]
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=f"{social_media} has no {social_type} type",
        )
    socials = await find_object_by_filter_and_paginate(filter_object, page, limit)
    count = await count_object(filter_object)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": socials, "total_record": count},
    )


@router.delete("/delete_social/{id}")
async def delete_user_social_media(id: str):
    deleted_social_media = await delete_user_by_id(id)
    if deleted_social_media:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.delete("/delete-priority/{id}")
async def delete_priority(id: str):
    deleted_user = await exec_delete_priority(id)
    if deleted_user:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.delete("/Social/{id}")
async def delete_user(id: str):
    deleted_user = await delete_user_by_id(id)
    if deleted_user:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.get("/{social_type}")
async def get_social_types(
    social_type: Optional[str] = Path(
        ..., title="Social Type", enum=["Object", "Group", "Fanpage"]
    ),
    social_name: str = "",
    page: int = 0,
    limit: int = 10,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    user = await find_user_by_id(ObjectId(user_id))
    if user is None:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": []})

    if "interested_list" not in user:
        client2.update_one(
            {"_id": ObjectId(user["_id"])}, {"$set": {"interested_list": []}}
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": []})

    filter = {"_id": {"$in": user["interested_list"]}}
    if social_type:
        filter["social_type"] = social_type
    if social_name:
        filter["social_name"] = {"$regex": f"{social_name.lower()}"}

    filter_object = {"social_type": social_type}
    if social_name:
        filter_object["social_name"] = {"$regex": f"{social_name}", "$options": "i"}
    # results = await find_object_by_filter_and_paginate(filter_object, page, limit)
    # count = await count_object(filter_object)
    # filter
    items = await find_object_by_filter(filter_object)
    objects = await find_object_by_filter(filter)
    results = [item for item in items if item not in objects]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            # "data": results,
            # filtered results
            "data": results,
        },
    )


@router.put("/update-priority")
async def update_priority(data: UpdatePriorityModel = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    updated_item = await exec_update_priority(data)
    if updated_item:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Successful edit",
        )
    return status.HTTP_403_FORBIDDEN


@router.put("/edit_social")
async def update_social_config(data: UpdateSocial = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    updated_social = await update_social_account(data)
    if updated_social:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Successful edit social config",
        )
    return status.HTTP_403_FORBIDDEN


@router.put("/add_followed_by")
async def update_followed_by_user(
    id_user: str, list_followeds: List[AddFollowed] = Body(...)
):
    id_obj = ObjectId(id_user)
    followeds = []
    for list_followed in list_followeds:
        followed = AddFollowed(
            followed_id=list_followed.followed_id, username=list_followed.username
        )
        followeds.append(followed)
    await update_followed_by(id_obj, followeds)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content="Successful edit")


@router.put("/delete_followed_by")
async def delete_followed_by_user(
    id_user: str, id_followeds: List[AddFollowed] = Body(...)
):
    id_obj = ObjectId(id_user)
    list_id_new = []
    for id_user in id_followeds:
        list_id_new.append(id_user)
    await delete_followed_by(id_obj, list_id_new)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content="Successful delete"
    )


@router.put("/edit_status")
async def update_status(id: str, data: UpdateStatus = Body(...)):
    data = {k: v for k, v in data.dict().items() if v is not None}
    updated_status = await update_status_account(id, data)
    if updated_status:
        return status.HTTP_200_OK
    return status.HTTP_403_FORBIDDEN


@router.post("/read")
async def read_socials(
    post_ids: List[str], social_platform: str, authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    result = await check_read_socials(post_ids, social_platform, user_id)
    return result


@router.post("/unread")
async def unread_socials(
    post_ids: List[str],
    social_platform: str,
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    await check_unread_socials(post_ids, social_platform, user_id)
    return post_ids


@router.post("/export-to-word")
async def export_to_word(news_ids: List[str], platform: str = "facebook"):
    news_social = await get_news_social(news_ids, platform)
    file_buff = export_social_word(news_social)
    nowstr = datetime.now().strftime("%d-%m-%Y")

    nameFile = (
        "facebook"
        if platform == "facebook"
        else ("twitter" if platform == "twitter" else "tiktok")
    )
    return Response(
        file_buff.read(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Access-Control-Expose-Headers": "Content-Disposition",
            "Content-Disposition": f"attachment; filename=su_kien({nameFile}-{nowstr}).docx",
        },
    )


@router.get("/post-detail/{_id}")
async def get_post_detail(_id: str):
    return await post_detail(_id)
