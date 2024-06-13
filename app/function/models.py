from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Union

class Function(BaseModel):
    function_id: str = Field(default_factory=ObjectId, alias="_id")
    function_code: str = Field(default_factory=lambda: str(ObjectId()))
    parent_id: Union[str, int] = 0
    function_name: str
    function_name_eng: str = ""
    url: str
    description: str
    sort_order: int
    level: int = 1



