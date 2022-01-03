"""Endpoint Users"""


from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User
from app.api import deps
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
        db: Session = Depends(deps.get_db)
):
    """Вывод пользователей"""
    data = crud.get_multi(db=db, model=User)
    return data


@router.post("/", response_model=List[schemas.User])
def create_user(
        user_in: schemas.UserBase,
        db: Session = Depends(deps.get_db)
):
    """Создание пользователя"""
    user = crud.get_by_login(db=db, model=User, login=user_in.login)

    if user:
        raise HTTPException(
            status_code=400,
            detail='User exists'
        )
    user = crud.create(db=db, model=User, obj_in=user_in)
    return user
