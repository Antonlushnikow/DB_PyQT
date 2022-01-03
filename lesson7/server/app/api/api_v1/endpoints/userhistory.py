"""Endpoint UserContacts"""

import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import UserHistory
from app.api import deps
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.UserHistory])
def read_user_history(
        db: Session = Depends(deps.get_db)
):
    """Вывод истории входа пользователей"""
    data = crud.get_multi(db=db, model=UserHistory)
    return data


@router.post("/", response_model=List[schemas.UserHistory])
def create_user_history(
        obj_in: schemas.UserHistory,
        db: Session = Depends(deps.get_db)
):
    """Добавление истории входа пользователя"""
    _ = crud.create(db=db, model=UserHistory, obj_in=obj_in)
    return