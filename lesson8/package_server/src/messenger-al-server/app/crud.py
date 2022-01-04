from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


def create(db: Session, model, obj_in):
    """Добавление записи в таблицу"""
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = model(**obj_in_data)
    db.add(db_obj)
    db.commit()
    return db_obj


def get_by_id(db: Session, model, id_: int):
    """Получение объекта модели по id"""
    return db.query(model).filter(model.id == id_).first()


def get_by_login(db: Session, model, login: str):
    """Получение объекта пользователя по логину"""
    obj = db.query(model).filter(model.login == login).first()
    return obj


def get_by_filter(db: Session, model, **kwargs):
    """Получение записей таблицы по фильтру"""
    return db.query(model).filter_by(**kwargs).all()


def get_multi(db: Session, model):
    """Получение всех записей таблицы"""
    return db.query(model).all()


def delete_by_id(db: Session, model, id_):
    """Удаление записи из таблицы по id"""
    db.query(model).filter(model.id == id_).delete()
    db.commit()
    return


def delete_by_filter(db: Session, model, **kwargs):
    """Удаление записи из таблицы по фильтру"""
    objects = db.query(model).filter_by(**kwargs)
    objects.delete()
    db.commit()
    return

