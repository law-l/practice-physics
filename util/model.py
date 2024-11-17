from pydantic_core import from_json
from pydantic import BaseModel
import os

class Problem(BaseModel):
    id: str
    question: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    answer: str
    explanation: str