from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    info: Optional[str] = None


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
