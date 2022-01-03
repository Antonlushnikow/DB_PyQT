from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


def get_by_id(db: Session, model, id_: int):
    """Получение объекта по id"""
    return db.query(model).filter(model.id == id_).first()


def get_by_login(db: Session, model, login: str):
    """Получение объекта по логину"""
    return db.query(model).filter(model.login == login).first()


def get_by_filter(db: Session, model, **kwargs):
    """Получение объектов по фильтру"""
    return db.query(model).filter_by(**kwargs).all()


def get_multi(db: Session, model):
    """Получение всех объектов таблицы"""
    objects = db.query(model)
    return objects.all()


def create(db: Session, model, obj_in):
    """Создание записи в таблице"""
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = model(**obj_in_data)
    db.add(db_obj)
    db.commit()
    return db_obj


def delete_by_filter(db: Session, model, **kwargs):
    """Удаление по фильтру"""
    objects = db.query(model).filter_by(**kwargs)
    objects.delete()
    db.commit()
    return
