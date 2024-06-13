from pydantic import BaseModel

class EmailModel(BaseModel):
    email: str