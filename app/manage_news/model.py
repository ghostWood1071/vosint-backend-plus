import re
from typing import Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class SourceSchema(BaseModel):
    id: Optional[str]
    name: str
    host_name: Optional[str]


class SourceGroupSchema(BaseModel):
    user_id: str
    source_name: str
    news: list[SourceSchema] = []
    is_hide: bool

    class config:
        orm_mode = True
