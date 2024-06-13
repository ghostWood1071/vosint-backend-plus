from vosint_ingestion.models import MongoRepository
from typing import *
from .models import InsertRolePermission
from bson.objectid import ObjectId
import traceback
from db.init_db import get_collection_client

def get_action_by_role_function_id(role_function_id)->List[Any]:
    try:
        search_params = {
            "collection_name": "role_permission",
            "filter_spec": {"role_function_id": role_function_id}, 
        }

        result, _ = MongoRepository().find(**search_params)
        for line in result:
            line["_id"] = str(line["_id"])

        return { "data": result }
    except Exception as e:
        traceback.print_exc()
        raise e

async def insert_role_permission(doc: dict) -> Any:
    try:
        role_function_id = doc.get("role_function_id")
        action_ids = doc.get("action_ids")

        if not role_function_id:
            raise ValueError("Role Function ID and action IDs are required")

        documents = [{"role_function_id": role_function_id, "action_id": action_id} for action_id in action_ids]

        # Delete existing documents
        del_count = MongoRepository().delete_many("role_permission", filter_spec={"role_function_id": role_function_id})

        # Insert documents asynchronously
        role_permission_client = get_collection_client("role_permission")
        if(len(action_ids) > 0):
            inserted_ids = await role_permission_client.insert_many(documents)

        return "inserted_ids"

    except Exception as e:
        traceback.print_exc()
        raise e