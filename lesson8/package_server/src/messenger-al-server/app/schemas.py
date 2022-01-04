from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """Базовый класс проверки данных"""
    login: str
    info: Optional[str] = None
    salt: str
    password_hash: str


class User(UserBase):
    """Класс проверки данных модели пользователя"""
    id: int

    class Config:
        orm_mode = True


class UserHistory(BaseModel):
    """Класс проверки данных модели истории входа"""
    user_id: int
    ip_addr: Optional[str] = None
    logon_time: Optional[datetime]

    class Config:
        orm_mode = True


class UserContact(BaseModel):
    """Класс проверки данных модели контактов пользователя"""
    user_id: int
    contact_id: int

    class Config:
        orm_mode = True
