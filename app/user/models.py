from enum import Enum
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from bson import ObjectId

class Role(str, Enum):
    admin = "admin"
    expert = "expert"
    leader = "leader"


class UserModal(BaseModel):
    username: str
    password: str
    full_name: str
    role: Role
    news_bookmarks: list[str]
    vital_list: list[str]
    interested_list: list[str]
    avatar_url: Optional[str]


class UserCreateModel(BaseModel):
    username: str
    password: str
    full_name: str
    role: Role


class UserUpdateModel(BaseModel):
    username: Optional[str]
    password: Optional[str]
    full_name: Optional[str]
    role: Optional[Role]
    avatar_url: Optional[str]
    online: Optional[bool]


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserChangePasswordModel(BaseModel):
    username: str
    password: str
    new_password: str


class InterestedModel(BaseModel):
    id: Optional[str] = Field(...)


class BaseUser(BaseModel):
    id: str
    online: bool

class User(BaseModel):
    user_id: str = Field(default_factory=ObjectId, alias="_id")
    branch_id: str = Field(None)
    department_id: str = Field(None)
    role_id: str = Field(None)
    username: str
    hashed_password: str = Field(None)
    password: Optional[str]
    full_name: str
    avatar_url: str = ""
    gender: int = 0
    date_of_birth: str = ""
    email: str = ""
    phone: str = ""
    online: bool = False
    description: str = ""
    active: int = 1
class ResetPasswordModel(BaseModel):
    new_password: str
    new_confirm_password: str
    username: str
    token: str
