from typing import Optional

from pydantic import BaseModel, Field


class CreateInfor(BaseModel):
    name: str
    host_name: str
    language: str
    publishing_country: str
    source_type: str
    event_detect: bool = True

    class config:
        orm_mode = True


class UpdateInfor(BaseModel):
    name: Optional[str]
    host_name: Optional[str]
    language: Optional[str]
    publishing_country: Optional[str]
    source_type: Optional[str]
    event_detect: bool = True

    class config:
        orm_mode = True
