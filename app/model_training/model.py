from pydantic import BaseModel, Field
from typing import *

class SearchParams(BaseModel):
    search_text:Optional[str] = Field(default=None)
    set_type:Optional[str] = Field(default=None)
    page_index:int = Field(default=1)
    page_size:int = Field(default=50)

class TrainParams(BaseModel):
    learning_rate: float = Field(default=0.00002)
    batch_size:int = Field(default=4)
    num_epoch:int = Field(default=10)
    output_model_name:str = Field(default="best_model")