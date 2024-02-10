from pydantic import BaseModel
from fastapi import UploadFile, File
from typing import Optional, Union
from datetime import date, datetime
from entities import State

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id_user: int | None = None


class UserData(BaseModel):
    id: int
    name : str
    password : str
    image: str

class CreateTask(BaseModel):
    text: str
    create_date : date = datetime.now().date()
    finish_date : date
    state : State = State.START
    category : int
    user : int

class TaskData(CreateTask):
    id: int
    class Config:
        orm_mode = True

class CreateCategory(BaseModel):
    name : str

class CategoryData(CreateCategory):
    id: int
    class Config:
        orm_mode = True