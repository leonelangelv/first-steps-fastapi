from pydantic import BaseModel
from typing import TypedDict


class Blog(BaseModel):
    title: str
    body: str


class ResponseBlog(BaseModel):
    id: int
    title: str
    body: str

    class Config:
        orm_mode = True


class UserData(TypedDict):
    username: str
    email: str
    password: str


class User(BaseModel):
    name: str
    email: str
    password: str

    def to_dict(self) -> UserData:
        return {"name": self.name, "email": self.email, "password": self.password}
