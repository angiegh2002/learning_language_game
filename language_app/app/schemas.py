from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List


model_config = {"from_attributes": True}
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class QuestionBase(BaseModel):
    word: str
    description: Optional[str]

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int

    class Config:
        orm_mode = True

class AnswerCheck(BaseModel):
    question_id: int
    answer: str


class QuestionStatsByDate(BaseModel):
    date: datetime
    count: int
class AnswerLogCreate(BaseModel):
    question_id: int
    is_correct: bool

class AnswerStatsByDate(BaseModel):
    date: datetime
    correct: int
    incorrect: int

class UserStatsByDate(BaseModel):
    date: datetime
    count: int

