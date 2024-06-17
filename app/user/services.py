import re
from typing import *
from bson.objectid import ObjectId
from app.list_object.service import object_to_json
from app.user.models import InterestedModel
from db.init_db import get_collection_client
import traceback
from vosint_ingestion.models import MongoRepository
from app.auth.password import get_password_hash

client = get_collection_client("users")

async def create_user(user):
    created_user = await client.insert_one(user)
    return await client.find_one({"id": created_user.inserted_id})


async def read_user_by_username(username: str):
    return await client.find_one({"username": username})


async def update_user(user_id: ObjectId, user):
    return await client.update_one({"_id": user_id}, {"$set": user})


async def get_users(filter_spec, skip: int, limit: int):
    offset = (skip - 1) * limit if skip > 0 else 0
    users = []
    async for new in client.find(filter_spec).sort("_id").skip(offset).limit(limit):
        new = user_entity(new)
        users.append(new)

    return users


async def count_users(filter_spec):
    return await client.count_documents(filter_spec)


async def get_user_by_id(id: ObjectId):
    return await client.find_one({"_id": id})


async def get_user(id: str) -> dict:
    users = await client.find_one({"_id": ObjectId(id)})
    if users:
        return user_entity(users)


async def find_user_by_id(user_id: str):
    return await client.find_one({"_id": user_id})


async def update_bookmark_user(id: ObjectId, datas: List[ObjectId]):
    return await client.update_one(
        {"_id": id}, {"$push": {"news_bookmarks": {"$each": datas}}}
    )


async def delete_bookmark_user(id: ObjectId, id_bookmarks: List[ObjectId]):
    return await client.update_one(
        {"_id": id}, {"$pull": {"news_bookmarks": {"$in": id_bookmarks}}}
    )


async def update_vital_user(id: ObjectId, vitals: List[ObjectId]):
    return await client.update_one(
        {"_id": id}, {"$push": {"vital_list": {"$each": vitals}}}
    )


async def delete_vital_user(id: ObjectId, id_vitals: List[ObjectId]):
    return await client.update_one(
        {"_id": id}, {"$pull": {"vital_list": {"$in": id_vitals}}}
    )


async def update_interested_object(
    user_id: ObjectId, interested_objects: List[ObjectId]
):
    return await client.update_one(
        {"_id": user_id}, {"$push": {"interested_list": {"$each": interested_objects}}}
    )


async def delete_item_from_interested_list(
    user_id: str, id_interesteds: List[ObjectId]
):
    return await client.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"interested_list": {"$in": id_interesteds}}},
    )


async def get_interested_list(social_name):
    pipeline = [
        {"$match": {"interested_list.social_name": {"$regex": social_name}}},
        {"$project": {"_id": 0, "interested_list": 1}},
        {"$unwind": "$interested_list"},
        {"$match": {"interested_list.social_name": {"$regex": social_name}}},
    ]
    cursor = client.aggregate(pipeline)
    interested_list = []
    async for document in cursor:
        interested_list.append(document["interested_list"])
    return interested_list


async def delete_user(id: str):
    user = await client.find_one({"_id": ObjectId(id)})
    if user:
        await client.delete_one({"_id": ObjectId(id)})
        return True


async def get_vital_ids(id: ObjectId):
    user = await client.find_one({"_id": ObjectId(id)})
    vital_ids = [str(vital_id) for vital_id in user["vital_list"]]
    return vital_ids


def user_entity(user) -> dict:
    news_bookmarks = []
    vital_list = []
    interested_list = []

    if "vital_list" in user:
        for news_id in user["vital_list"]:
            vital_list.append(str(news_id))

    if "news_bookmarks" in user:
        for news_id in user["news_bookmarks"]:
            news_bookmarks.append(str(news_id))

    if "interested_list" in user:
        for object_id in user["interested_list"]:
            interested_list.append(str(object_id))

    return {
        "_id": str(user["_id"]),
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user.get("role"),
        "news_bookmarks": news_bookmarks,
        "vital_list": vital_list,
        "interested_list": interested_list,
        "avatar_url": user["avatar_url"] if "avatar_url" in user else None,
    }

########################### PLUS #################################
def get_users(text_search:str, page_size:int, page_index:int, branch_id: str, department_id: str, role_id: str)->List[Any]:
    try:
        # Calculate skip based on page_index and page_size
        skip = page_size * (page_index - 1)

        # Define filter specifications
        filter_spec = {}

        # Update filter_spec for text search
        if text_search:
            filter_spec["$or"] = [
                {"full_name": {"$regex": text_search, "$options": "i"}},
                {"username": {"$regex": text_search, "$options": "i"}},
                {"phone": {"$regex": text_search, "$options": "i"}},
                {"email": {"$regex": text_search, "$options": "i"}}
            ]

        # Update filter_spec for branch_id
        if branch_id:
            filter_spec["branch_id"] = branch_id

        # Update filter_spec for department_id
        if department_id:
            filter_spec["department_id"] = department_id

        # Update filter_spec for role_id
        if department_id:
            filter_spec["role_id"] = role_id

        # Define aggregation pipeline
        aggregation_pipeline = [
            {"$match": filter_spec},
            {"$lookup": {
                "from": "branch",   
                "let": {"branch_id": {"$toObjectId": "$branch_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$branch_id"]}}}
                ],
                "as": "branch"
            }},
            {"$unwind": {"path": "$branch", "preserveNullAndEmptyArrays": True}}, 
            {"$lookup": {
                "from": "department", 
                "let": {"department_id": {"$toObjectId": "$department_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$department_id"]}}}
                ],
                "as": "department"         
            }},
            {"$unwind": {"path": "$department", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "role", 
                "let": {"role_id": {"$toObjectId": "$role_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$role_id"]}}}
                ],
                "as": "role"         
            }},
            {"$unwind": {"path": "$role", "preserveNullAndEmptyArrays": True}},
            {"$skip": skip},  
            {"$limit": page_size},
            {
                "$project": {
                    "_id": {"$toString": "$_id"}, 
                    "full_name": 1, "username": 1, "phone": 1, "email": 1, "avatar_url": 1, "active": 1,
                    "branch_name": "$branch.branch_name",
                    "department_name": "$department.department_name",
                    "role_name": "$role.role_name"
                }
            }
        ]

        # Perform the query
        result, total_docs = MongoRepository().aggregate("users", aggregation_pipeline)

        # Convert ObjectId to str if needed
        for line in result:
            line["_id"] = str(line["_id"])

        # Return the result
        return {"data": result, "total_records": total_docs}


    except Exception as e:
        traceback.print_exc()
        raise e

def get_user(user_id:str)->Any:
    try:
        result, _ = MongoRepository().find("users", filter_spec={"_id": ObjectId(user_id)})
        if len(result) == 0:
            raise Exception(f"User {user_id} no found")

        result[0]["_id"] = str(result[0]["_id"])
        return result[0]
    except Exception as e:
        traceback.print_exc()
        raise e

def delete_users(user_ids:list[str])->Any:
    try:
        del_condition = [ObjectId(x) for x in user_ids]
        del_count = 0
        if len(del_condition) > 0:
            del_count = MongoRepository().delete_many("users", filter_spec={"_id": {"$in": del_condition}})
        return del_count
    except Exception as e:
        traceback.print_exc()
        raise e

def update_user(user_id:str, update_val:dict[str, Any])->Any:
    try:

        if "password" in update_val and update_val["password"] is not None:
            update_val["hashed_password"] = get_password_hash(update_val["password"])

        update_count = 0
        if update_val.get("user_id"):
            update_val.pop("user_id")

        
        update_params = {
            "collection_name": "users",
            "filter_spec": {
                "_id": ObjectId(user_id)
            },
            "action": {
                "$set": update_val
            }
        }
        update_count = MongoRepository().update_many(**update_params)
        return update_count
    except Exception as e:
        traceback.print_exc()
        raise e

def insert_user(doc:dict[Any])->Any:
    try:
        if doc.get("user_id"):
            doc.pop("user_id")

        doc["hashed_password"] = get_password_hash(doc["hashed_password"])

        inserted_id = MongoRepository().insert_one("users", doc)
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise e