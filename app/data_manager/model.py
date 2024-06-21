from pydantic import BaseModel, Field
from typing import *


class SearchItemParams(BaseModel):
    search_text:str = Field(default=None)
    end_date:str = Field(default=None)
    start_date:str = Field(default=None)
    catalog_id:str = Field(default=None)
    page_index: int = Field(default=1)
    page_size: int =Field(default=50)


class Doc(BaseModel):
    catalog_id: str = ""
    source_favicon: Optional[str] = ""
    source_name: Optional[str] = ""
    source_host_name: Optional[str] = ""
    source_language: Optional[str] = ""
    source_publishing_country: Optional[str] = ""
    source_source_type: Optional[str] = ""
    data_class_chude: List[str] = Field(default_factory=list, alias="data:class_chude")
    data_class_linhvuc: List[str] = Field(default_factory=list, alias="data:class_linhvuc")
    data_title: Optional[str] = Field("", alias="data:title")
    data_content: Optional[str] = Field("", alias="data:content")
    pub_date: Optional[str] = ""
    data_url: Optional[str] = Field(None, alias="data:url")
    data_author: Optional[str] = Field("", alias="data:author")
    data_time: Optional[str] = Field("", alias="data:time")
    data_html: Optional[str] = Field("", alias="data:html")
    data_title_translate: Optional[str] = Field("", alias="data:title_translate")
    data_content_translate: Optional[str] = Field("", alias="data:content_translate")
    keywords: List[str] = Field(default_factory=list)
    data_class_sacthai: Optional[str] = Field("0", alias="data:class_sacthai")
    data_summaries: Dict[str, Any] = Field(default={})
    summarize_s60: Optional[str] = ""