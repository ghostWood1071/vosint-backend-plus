from pydantic import BaseModel, Field
from bson import ObjectId
from typing import * 

class RoleFunction(BaseModel):
    role_function_id: str = Field(default_factory=ObjectId, alias="_id")
    function_id: str
    role_id: str

class InsertRoleFunction(BaseModel):
    role_id: str
    function_ids: List[str]
