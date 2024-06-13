from typing import List, Optional

from pydantic import BaseModel, Field


class UserConfig(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
    list_proxy: List = Field(...)
