from pydantic import BaseModel, Field
from bson import ObjectId
from typing import *

class Catalog(BaseModel):
    catalog_id: str = Field(default_factory=ObjectId, alias="_id")
    catalog_name: str
    description: str
    picture: str
    sort_order: int = 1
    created_at: Optional[str]

