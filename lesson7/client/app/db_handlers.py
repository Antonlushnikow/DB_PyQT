from app import crud
from app.api import deps
from app.models import User, UserContact, MessageHistory


def create_user(login, info):
    """Создание пользователя"""
    obj = crud.create(db=next(deps.get_db()), model=User, obj_in={'login': login, 'info': info})


def add_message(user, contact, message):
    """Добавление сообщения в историю"""
    _ = crud.create(db=next(deps.get_db()), model=MessageHistory,
                    obj_in={'user': user, 'contact': contact, 'message': message})


def add_contact(user, contact):
    """Добавление контакта"""
    _ = crud.create(db=next(deps.get_db()), model=UserContact, obj_in={'user': user, 'contact': contact})


def get_contacts(user):
    """Получение контактов пользователя"""
    filter_ = {'user': user}
    objects = crud.get_by_filter(next(deps.get_db()), UserContact, **filter_)
    contacts = []
    for obj in objects:
        contacts.append(obj.contact)
    return contacts


def delete_contacts(user):
    """Удаляет все записи в таблице контактов"""
    filter_ = {'user': user}
    _ = crud.delete_by_filter(next(deps.get_db()), UserContact, **filter_)


def del_contact(user, contact):
    """Удаляет один контакт"""
    try:
        filter_ = {'user': user, 'contact': contact}
        _ = crud.delete_by_filter(next(deps.get_db()), UserContact, **filter_)
    except:
        print('Contact doesnt exist')


def get_last_messages(user, contact):
    """Получение последних пяти сообщений"""
    objects = next(deps.get_db()).query(MessageHistory).filter(
        ((MessageHistory.user == user) & (MessageHistory.contact == contact)) | \
        ((MessageHistory.user == contact) & \
         (MessageHistory.contact == user))).order_by(MessageHistory.time.desc()).limit(5)
    last_messages = []
    for obj in objects:
        last_messages.append((obj.time.strftime("%d-%m-%Y %H:%M:%S"), obj.user, obj.message))
    return last_messages
