from pydantic import BaseModel, Field
from bson import ObjectId

class Role(BaseModel):
    role_id: str = Field(default_factory=ObjectId, alias="_id")
    role_code: str
    role_name: str
    description: str
