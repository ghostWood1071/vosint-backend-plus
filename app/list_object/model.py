from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Status(str, Enum):
    enable = "enable"
    disable = "disable"


class Type(str, Enum):
    object = "Đối tượng"
    organization = "Tổ chức"
    nation = "Quốc gia"


class Keyword(BaseModel):
    vi: str = Field(...)
    en: str = Field(...)
    ru: str = Field(...)
    cn: str = Field(...)


class CreateObject(BaseModel):
    name: str = Field(...)
    facebook_link: str = Field(...)
    twitter_link: str = Field(...)
    profile_link: str = Field(...)
    avatar_url: str = Field(...)
    profile: str = Field(...)
    keywords: Keyword
    object_type: str = Field(...)
    status: str = Field(...)

    class config:
        orm_mode = True


class UpdateObject(BaseModel):
    name: Optional[str]
    facebook_link: Optional[str]
    twitter_link: Optional[str]
    profile_link: Optional[str]
    avatar_url: Optional[str]
    profile: Optional[str]
    keywords: Keyword
    object_type: Optional[str]
    status: Optional[str]

    class config:
        orm_mode = True
