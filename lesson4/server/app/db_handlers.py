from api import deps
import crud
from models import User, UserHistory


def create_user(login, info):
    obj = crud.create(db=next(deps.get_db()), model=User, obj_in={'login': login, 'info': info})


def get_obj_by_login(login):
    obj = crud.get_by_login(db=next(deps.get_db()), model=User, login=login)
    return obj


def add_history(user_id, ip_addr=''):
    obj = crud.create(db=next(deps.get_db()), model=UserHistory, obj_in={'user_id': user_id, 'ip_addr': ip_addr})

