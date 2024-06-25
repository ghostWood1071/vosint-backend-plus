from pydantic import BaseModel, Field
from typing import *

class Word(BaseModel):
    value:str = Field(default="")
    synonyms:List[str] = Field(default=[])
    multimeans:List[str] = Field(default=[])

class WordUpdate(Word):
    id: str = Field("", alias="word_id") 
    mode:int = Field(default=0, ge=0, le=1, description="0: update synonyms; 1: update multimeans")


class SearchParams(BaseModel):
    search_text:Optional[str] = Field(default=None)
    mode:int = Field(default=0, ge=0, le=1, description="0: update synonyms; 1: update multimeans")
    page_size:int = Field(default=50)
    page_index:int = Field(default=1)