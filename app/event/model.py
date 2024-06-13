from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AddNewEvent(BaseModel):
    id_new: str
    data_title: str
    data_url: str


class NewsUser(BaseModel):
    id: str
    title: str
    link: str


class Report(BaseModel):
    id: str
    title: str
    public: bool = False


class CreateEvent(BaseModel):
    event_name: str = Field(...)
    event_content: Optional[str]
    date_created: Optional[str]
    new_list: Optional[List] = []
    system_created: bool = False
    chu_the: Optional[str]
    khach_the: Optional[str]
    user_id: Optional[str]
    total_new: Optional[str]
    list_linh_vuc: Optional[List] = []
    news_added_by_user: Optional[List[NewsUser]]
    list_report: Optional[List] = []

    class config:
        orm_mode = True


class UpdateEvent(BaseModel):
    event_name: Optional[str] = Field(...)
    event_content: Optional[str]
    date_created: Optional[str]
    new_list: Optional[List] = []
    system_created: bool = False
    chu_the: Optional[str]
    khach_the: Optional[str]
    user_id: Optional[str]
    total_new: Optional[str]
    list_linh_vuc: Optional[List] = []
    news_added_by_user: Optional[List[NewsUser]]
    list_report: Optional[List] = []
