from pydantic import BaseModel
from typing import *


class Summarize(BaseModel):
    lang: str
    title: str
    paras: str
    k: float
