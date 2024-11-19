from pydantic import BaseModel


class Problem(BaseModel):
    id: int
    topic: str
    question: str
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    answer: str
    explanation: str
