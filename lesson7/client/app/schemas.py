from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """Базовый класс проверки данных"""
    login: str
    info: Optional[str] = None


class User(UserBase):
    """Класс проверки данных модели пользователя"""
    id: int

    class Config:
        orm_mode = True
