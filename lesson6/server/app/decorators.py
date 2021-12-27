import inspect
import logging
import sys
from project_logs.config import server_log_config

LOG = logging.getLogger('app.server')


def log(func):
    def wrapper(*args, **kwargs):
        LOG.debug(
            f'Вызов функции {func.__name__} с параметрами {args}, {kwargs}. '
            f'Вызвана из файла {inspect.stack()[1][1]}, модуля {func.__module__}, '
            f'функции {inspect.stack()[1][3]}', stacklevel=2)
        return func(*args, **kwargs)
    return wrapper


def login_required(func, obj):
    def wrapper(*args, **kwargs):
        print(obj)
        return func(*args, **kwargs)
    return wrapper
