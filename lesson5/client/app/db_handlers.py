from api import deps
import crud
from models import User, UserContact, MessageHistory


def create_user(login, info):
    obj = crud.create(db=next(deps.get_db()), model=User, obj_in={'login': login, 'info': info})


def add_message(user_id, contact_id, message):
    obj = crud.create(db=next(deps.get_db()), model=MessageHistory, obj_in={'user': user_id, 'contact': contact_id, 'message': message})


def add_contact(user_id, contact_id):
    obj = crud.create(db=next(deps.get_db()), model=UserContact, obj_in={'user': user_id, 'contact': contact_id})
