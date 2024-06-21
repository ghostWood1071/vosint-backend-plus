from pydantic import BaseModel, Field

class HistoryLog(BaseModel):
    _id:str = Field("", description="id of action")
    actor_name:str = Field("user", description="name of user")
    actor_role:str = Field("some thing ...", description="id of role")
    action_name:str = Field("GET", description="name of action")
    target_type:str = Field("", description="type of target")
    target_name:str = Field("", description="name of target")

class SearchParams(BaseModel):
    text_search:str=Field(None)
    start_date:str=Field(None)
    end_date:str=Field(None)
    page_size:int = Field(50)
    page_index:int= Field(1)