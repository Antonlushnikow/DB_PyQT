from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    login: str
    info: Optional[str] = None


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserHistory(BaseModel):
    user_id: int
    ip_addr: Optional[str] = None
    logon_time: datetime

    class Config:
        orm_mode = True
