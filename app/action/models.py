from pydantic import BaseModel, Field
from bson import ObjectId

class Action(BaseModel):
    action_id: str = Field(default_factory=ObjectId, alias="_id")
    action_code: str
    function_id: str
    action_name: str
    description: str
