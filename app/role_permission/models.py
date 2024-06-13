from pydantic import BaseModel, Field
from bson import ObjectId
from typing import * 

class RolePermission(BaseModel):
    role_permission_id: str = Field(default_factory=ObjectId, alias="_id")
    role_function_id: str
    action_id: str

class InsertRolePermission(BaseModel):
    role_function_id: str
    action_ids: List[str]
