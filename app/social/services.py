from typing import List, Optional

from bson import ObjectId
from fastapi import status

from app.social.models import AddFollow, UpdateAccountMonitor
from db.init_db import get_collection_client
import json
from vosint_ingestion.utils import get_time_now_string

client = get_collection_client("socials")
client2 = get_collection_client("social_media")


async def get_all_user(skip: Optional[int] = None, limit: Optional[int] = None):
    users = []
    if limit is not None:
        async for user in client.find().limit(limit).skip(limit * (skip or 0)):
            users.append(user)
    else:
        async for user in client.find():
            users.append(user)
    return users


async def get_user(id: str) -> dict:
    users = await client.find_one({"_id": ObjectId(id)})
    if users:
        return users


async def create_user(user):
    created_user = await client.insert_one(user)
    new_user_id = str(created_user.inserted_id)
    filter_result = await client.find_one({"_id": ObjectId(new_user_id)})
    username = filter_result["username"]
    # update the followed_by list for each followed
    followeds = user.get("users_follow", [])
    await client2.update_many(
        {
            "_id": {
                "$in": [ObjectId(followed.get("follow_id")) for followed in followeds]
            }
        },
        {
            "$push": {
                "followed_by": {
                    "followed_id": new_user_id,
                    "username": username,
                }
            }
        },
    )
    return await client.find_one({"id": created_user.inserted_id})


async def delete_user(id: str):
    str_id = str(id)
    user = await client.find_one({"_id": ObjectId(id)})
    username = user["username"]
    followeds = []
    filter_object = user.get("users_follow")
    for filter_list in filter_object:
        followeds.append(
            {
                "follow_id": str(filter_list.get("follow_id")),
                "social_name": str(filter_list.get("social_name")),
            }
        )
    await client2.update_many(
        {"_id": {"$in": [ObjectId(f["follow_id"]) for f in followeds]}},
        {
            "$pull": {
                "followed_by": {
                    "followed_id": str_id,
                    "username": username,
                }
            }
        },
    )
    if user:
        await client.delete_one({"_id": ObjectId(id)})
        return True


async def update_username_user(id: str, username_new: str):
    user = await client.find_one({"_id": ObjectId(id)})
    user_id = str(id)
    followeds = user.get("users_follow", [])
    await client2.update_many(
        {"_id": {"$in": [ObjectId(followed["follow_id"]) for followed in followeds]}},
        {"$set": {f"followed_by.$[elem].username": username_new}},
        array_filters=[{"elem.followed_id": user_id}],
    )
    if user:
        await client.update_one(
            {"_id": ObjectId(id)}, {"$set": {"username": username_new}}
        )
        return True
    return False


async def update_follow_user(id: str, data: List[AddFollow]):
    user_id = str(id)
    filter_result = await client.find_one({"_id": ObjectId(id)})
    username = filter_result["username"]
    followeds = []
    for datum in data:
        followeds.append(
            {"follow_id": datum.follow_id, "social_name": datum.social_name}
        )
    await client2.update_many(
        {"_id": {"$in": [ObjectId(f["follow_id"]) for f in followeds]}},
        {"$addToSet": {"followed_by": {"followed_id": user_id, "username": username}}},
    )

    return await client.update_one(
        {"_id": ObjectId(id)},
        {"$addToSet": {"users_follow": {"$each": [datum.dict() for datum in data]}}},
    )


async def delete_follow_user(id: ObjectId, data: List[AddFollow]):
    user_id = str(id)
    filter_result = await client.find_one({"_id": ObjectId(id)})
    username = filter_result["username"]
    followeds = []
    for datum in data:
        followeds.append(
            {
                "follow_id": str(datum.follow_id),
                "social_name": datum.social_name,
            }
        )
    await client2.update_many(
        {"_id": {"$in": [ObjectId(f["follow_id"]) for f in followeds]}},
        {
            "$pull": {
                "followed_by": [
                    {
                        "followed_id": user_id,
                        "username": username,
                    }
                ]
            }
        },
    )
    docs = [dict(datum) for datum in data]
    return await client.update_one(
        {"_id": id}, {"$pull": {"users_follow": {"$in": docs}}}
    )


async def update_account_monitor(data: UpdateAccountMonitor):
    _id = data["id"]
    user_id = str(_id)
    socials = await client.find_one({"_id": ObjectId(_id)})
    username = socials["username"]
    compare_name = data["username"]
    if username != compare_name:
        username = compare_name
    users_follow = data.get("users_follow", [])

    await client2.update_many(
        {
            "followed_by.followed_id": user_id,
            "followed_by.username": username,
        },
        {
            "$pull": {
                "followed_by": {
                    "followed_id": user_id,
                    "username": username,
                }
            }
        },
    )

    for user_follow in users_follow:
        user_follow_id = user_follow.get("follow_id")
        await client2.update_one(
            {"_id": ObjectId(user_follow_id)},
            {
                "$addToSet": {
                    "followed_by": {
                        "followed_id": user_id,
                        "username": username,
                    }
                }
            },
        )

    data_copy = data.copy()
    data_copy.pop("id")

    return await client.update_one(
        {"_id": ObjectId(_id)},
        {"$set": data_copy},
    )


async def get_account_monitor_by_media(
    social_media: str, page: int = 1, limit: int = 20
):
    offset = (page - 1) * limit if page > 0 else 0
    list_social_media = []
    async for item in client.find(social_media).sort("_id").skip(offset).limit(limit):
        item = To_json(item)
        list_social_media.append(item)
    return list_social_media


def To_json(media) -> dict:
    media["_id"] = str(media["_id"])
    return media


async def count_object(filter_object):
    return await client.count_documents(filter_object)

async def get_account_dicts(news):
    account_links = []
    account_dict = {}
    for n in news:
        account_dict[n.get("account_link")] = ""
    account_links = list(account_dict.keys())
    accounts = {row.get("account_link"): str(row.get("_id")) async for row in client2.find({"account_link": {"$in": account_links}}, {"account_link": True, "_id": True})}
    n_exists = {acc:"" for acc in account_links if accounts.get(acc) is None}
    return accounts, n_exists



async def get_account_dict(news):
    news_dict = {}
    for x in news:
        news_dict[x.get("account_link")] = {
            "social_name": x.get("header"),
            "social_media": x.get("social_media"),
            "social_type": x.get("social_type"),
            "account_link": x.get("account_link"),
            "avatar_url": "",
            "profile": "",
            "is_active": True,
            "followed_by": []
        }
    exists, n_exists = await get_account_dicts(news)
    for link in list(n_exists.keys()):
        insert_result = await client2.insert_one(news_dict[link])
        n_exists[link] = str(insert_result.inserted_id)
    return {**exists, **n_exists}
    
        

async def get_not_exists_account(news):
    account_links = []
    for n in news:
        account_links.append(n.get("account_link"))
    accounts = {row.get("account_link"): 0 async for row in client2.find({"account_link": {"$in": account_links}}, {"account_link": True})}
    n_exists = {acc:"" for acc in account_links if accounts.get(acc) is None}
    return n_exists

async def handle_news_files(content):
    sample = {
        "social_type": "Object", #loại tài khoản, Object/Fanpage/Group,
        "social_media": "Facebook", #loai tin mxh
        "account_link": "", # url trang cá nhân 
        "header": "", #tên đối tượng
        "footer_date": "01/02/2024", #ngày đăng dd/mm/yyyy
        "content": "", # nộid dung bài đăng
        "link": "", #url bài viết
        "video_link": [], #link video
        "image_link": [], #link ảnh
        "other_link": [], #các đường dẫn khác
        "like": 0, #số lượng like
        "comments": "0", #số lượng comment
        "share": "0", #số lượng share 
        "id_data_ft": "", #cái này không cần điền
        "post_id": "", #id bài viết
        "footer_type": "page",
        "id_social": "", #object_id id của đối tượng cái này không cần điền
        "sentiment": "0", #sắc thái tin 0:trung tính, 1:tích cực, 2: tiêu cực
        "keywords": [], #danh sách từ khóa
    }
    data = json.loads(content)
    account_dict = await get_account_dict(data)
    social_clients = {
        "Facebook": get_collection_client("facebook"),
        "Twitter": get_collection_client("twitter"),
        "Tiktok": get_collection_client("tiktok"),
    }
    index = 0
    time = get_time_now_string()
    for row in data:
        try:
            row["id_social"] = ObjectId(account_dict.get(row["account_link"]))
            row["post_id"] = account_dict.get(row["account_link"]) + row["post_id"]
            row["create_at"] = time
            social_clients.get(row["social_media"]).insert_one(row)
            index+=1
        except Exception as e:
            raise Exception(f"error occur in record number: {index}-{str(e)}")
    return f"inserted {index} records"
    
    