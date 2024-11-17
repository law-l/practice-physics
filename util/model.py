import os

from pydantic import BaseModel
from pydantic_core import from_json


class Problem(BaseModel):
    id: int
    question: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    answer: str
    explanation: str
