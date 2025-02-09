from pydantic import BaseModel, Field
from bson import ObjectId

class Department(BaseModel):
    department_id: str = Field(default_factory=ObjectId, alias="_id")
    department_name: str
    phone: str
    fax: str
    address: str
