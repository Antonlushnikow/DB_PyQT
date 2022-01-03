import inspect
import logging
from functools import wraps


LOG = logging.getLogger('app.client')


def log(func):
    """Декоратор логирования"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        LOG.debug(
            f'Вызов функции {func.__name__} с параметрами {args}, {kwargs}. '
            f'Вызвана из файла {inspect.stack()[1][1]}, модуля {func.__module__}, '
            f'функции {inspect.stack()[1][3]}', stacklevel=2)
        return func(*args, **kwargs)
    return wrapper


def login_required(func):
    """Декоратор, проверяющий авторизацию пользователя"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args[0].is_authenticated:
            return func(*args, **kwargs)
        return args[0].stop(*args, **kwargs)
    return wrapper
