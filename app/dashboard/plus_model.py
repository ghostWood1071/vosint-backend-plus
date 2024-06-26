from pydantic import BaseModel, Field
from typing import *

class GetSourceListParams(BaseModel):
    group_id:Optional[str] = Field(default=None)
    order_by:List[str]=[]
    page_index:int=1
    page_size:int=50