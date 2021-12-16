from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


def get_by_id(db: Session, model, id: int):
    return db.query(model).filter(model.id == id).first()


def get_by_login(db: Session, model, login: str):
    return db.query(model).filter(model.login == login).first()


def get_multi(db: Session, model, sort=None, filter_=None):
    objects = db.query(model)
    return objects.all()


def create(db: Session, model, obj_in):
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = model(**obj_in_data)
    db.add(db_obj)
    db.commit()
    return db_obj
