from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.user.models import Role


class UserModel(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")
    username: str = Field(...)
    hash_password: str = Field(...)
    social: str


class AddFollow(BaseModel):
    follow_id: str
    social_name: str


class AddProxy(BaseModel):
    proxy_id: str
    name: str
    ip_address: str
    port: str


class UserCreateModel(BaseModel):
    username: Optional[str]
    password: Optional[str]
    social: str = Field(...)
    users_follow: List[AddFollow]
    list_proxy: List[AddProxy]
    cookie: str = Field(...)
    cron_expr: str = Field(...)
    enabled: bool = False


class UpdateAccountMonitor(BaseModel):
    id: str
    username: Optional[str]
    password: Optional[str]
    social: str = Field(...)
    users_follow: List[AddFollow]
    list_proxy: List[AddProxy]
    cookie: str = Field(...)
    cron_expr: str = Field(...)
    enabled: bool = False
