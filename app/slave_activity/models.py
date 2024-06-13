from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class SlaveActivity(BaseModel):
    id: str = Field(...)
    url: str = Field(...)
    source: str = Field(...)
    created_at: str = Field(...)
