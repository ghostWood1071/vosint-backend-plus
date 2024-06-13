from bson import ObjectId

from db.init_db import get_collection_client

client = get_collection_client("user_config")

async def get_all_user():
    users = []
    async for item in client.find():
        users.append(item)
    return users
    
async def update_user_config(id: str, data: dict):
    await client.update_one({"_id": ObjectId(id)} ,{"$set": data})
