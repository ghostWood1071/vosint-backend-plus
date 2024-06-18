from pydantic import BaseModel, Field
from bson import ObjectId

class Branch(BaseModel):
    branch_id: str = Field(default_factory=ObjectId, alias="_id")
    branch_name: str
    phone: str
    fax: str = ""
    address: str
