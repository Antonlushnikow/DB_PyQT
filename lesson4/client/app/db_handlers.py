from app.api import deps
import crud
from models import User


def create_user(login, info):
    obj = crud.create(db=next(deps.get_db()), model=User, obj_in={'login': login, 'info': info})

