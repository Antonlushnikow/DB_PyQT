import inspect
import logging
import sys
from project_logs.config import client_log_config

if 'client' in sys.argv[0]:
    LOG = logging.getLogger('app.client')
else:
    LOG = logging.getLogger('app.server')


def log(func):
    def wrapper(*args, **kwargs):
        LOG.debug(
            f'Вызов функции {func.__name__} с параметрами {args}, {kwargs}. '
            f'Вызвана из файла {inspect.stack()[1][1]}, модуля {func.__module__}, '
            f'функции {inspect.stack()[1][3]}', stacklevel=2)
        return func(*args, **kwargs)
    return wrapper
