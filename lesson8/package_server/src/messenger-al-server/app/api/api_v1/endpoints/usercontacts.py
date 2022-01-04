"""Endpoint UserContacts"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import User, UserContact
from app.api import deps
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.UserContact])
def read_user_contacts(
        db: Session = Depends(deps.get_db)
):
    """Чтение списка контактов"""
    data = crud.get_multi(db=db, model=UserContact)
    return data


@router.post("/", response_model=List[schemas.UserContact])
def create_user_contact(
        obj_in: schemas.UserContact,
        db: Session = Depends(deps.get_db)
):
    """Создание контакта"""
    filter_ = {'user_id': obj_in.user_id, 'contact_id': obj_in.contact_id}
    obj = crud.get_by_filter(db=db, model=UserContact, **filter_)

    if obj:
        raise HTTPException(
            status_code=400,
            detail='Contact exists'
        )
    _ = crud.create(db=db, model=UserContact, obj_in=obj_in)
    return
