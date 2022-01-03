from app.api import deps
from app import crud
from app.models import User, UserHistory, UserContact


def create_user(login, passwd, salt, info):
    """Создание нового пользователя"""
    obj = crud.create(db=next(deps.get_db()),
                      model=User,
                      obj_in={'login': login, 'info': info, 'salt': salt, 'password_hash': passwd}
                      )
    return obj


def get_obj_by_login(login):
    """Получение объекта пользователя по логину"""
    obj = crud.get_by_login(db=next(deps.get_db()),
                            model=User,
                            login=login)
    return obj


def add_history(user_id, ip_addr=''):
    """Добавление записи в таблицу UserHistory"""
    _ = crud.create(db=next(deps.get_db()),
                    model=UserHistory,
                    obj_in={'user_id': user_id, 'ip_addr': ip_addr}
                    )


def add_contact(user_id, contact_id):
    """Добавление записи в таблицу UserContact"""
    try:
        _ = crud.create(db=next(deps.get_db()),
                          model=UserContact,
                          obj_in={'user_id': user_id, 'contact_id': contact_id})
    except:
        print('Contact exists')


def delete_contact(user_id, contact_id):
    """Удаление записи из таблицы UserContact"""
    try:
        filter_ = {'user_id': user_id, 'contact_id': contact_id}
        crud.delete_by_filter(next(deps.get_db()), UserContact, **filter_)
    except:
        print('Contact doesnt exist')


def get_contacts(user_id):
    """Получение контактов пользователя"""
    filter_ = {'user_id': user_id}
    objects = crud.get_by_filter(next(deps.get_db()), UserContact, **filter_)
    contacts = []
    for obj in objects:
        contacts.append(crud.get_by_id(next(deps.get_db()), User, obj.contact_id))
    return contacts
