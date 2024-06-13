from datetime import datetime

from pydantic import BaseModel, Field


class NewsModel(BaseModel):
    created_at: datetime = Field(alias="created_at")
    data_author: str = Field(alias="data:author")
    data_content: str = Field(alias="data:content")
    data_time: str = Field(alias="data:time")
    data_title: str = Field(alias="data:title")
    data_url: str = Field(alias="data:url")
    modified_at: datetime = Field(alias="modified_at")
