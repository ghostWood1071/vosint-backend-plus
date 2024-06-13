from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class AddFollowed(BaseModel):
    followed_id: str
    username: str


class CreatePriorityModel(BaseModel):
    priority_name: str = Field(...)
    avatar_url: Optional[str] = ""
    description: Optional[str] = ""
    facebook: Optional[str] = ""
    twitter: Optional[str] = ""
    tiktok: Optional[str] = ""


class UpdatePriorityModel(BaseModel):
    id: str
    priority_name: str = Field(...)
    avatar_url: Optional[str] = ""
    description: Optional[str] = ""
    facebook: Optional[str] = ""
    twitter: Optional[str] = ""
    tiktok: Optional[str] = ""


class CreateSocialModel(BaseModel):
    social_name: str = Field(...)
    social_media: str = Field(...)
    social_type: str = Field(...)
    account_link: str
    avatar_url: str = Field(...)
    profile: str = Field(...)
    is_active: bool = True
    followed_by: List[AddFollowed]

    class config:
        orm_mode = True


class UpdateSocial(BaseModel):
    id: str
    social_name: Optional[str] = Field(...)
    social_media: Optional[str] = Field(...)
    social_type: Optional[str] = Field(...)
    account_link: Optional[str]
    avatar_url: Optional[str] = Field(...)
    profile: Optional[str] = Field(...)
    is_active: Optional[bool]
    followed_by: List[AddFollowed]


class UpdateStatus(BaseModel):
    is_active: bool = True
