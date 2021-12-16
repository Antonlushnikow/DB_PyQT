from api import deps
import crud
from models import User, UserHistory, UserContact


def create_user(login, info):
    obj = crud.create(db=next(deps.get_db()), model=User, obj_in={'login': login, 'info': info})


def get_obj_by_login(login):
    obj = crud.get_by_login(db=next(deps.get_db()), model=User, login=login)
    return obj


def add_history(user_id, ip_addr=''):
    obj = crud.create(db=next(deps.get_db()), model=UserHistory, obj_in={'user_id': user_id, 'ip_addr': ip_addr})


def add_contact(user_id, contact_id):
    try:
        obj = crud.create(db=next(deps.get_db()), model=UserContact, obj_in={'user_id': user_id, 'contact_id': contact_id})
    except:
        print('Contact exists')


def delete_contact(user_id, contact_id):
    try:
        filter_ = {'user_id': user_id, 'contact_id': contact_id}
        obj = crud.delete_by_filter(next(deps.get_db()), UserContact, **filter_)
    except:
        print('Contact doesnt exist')


def get_contacts(user_id):
    filter_ = {'user_id': user_id}
    objects = crud.get_by_filter(next(deps.get_db()), UserContact, **filter_)
    contacts = []
    for obj in objects:
        contacts.append(crud.get_by_id(next(deps.get_db()), User, obj.contact_id))
    return contacts
