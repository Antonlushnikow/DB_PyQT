import logging
from common.constants import DEFAULT_PORT


LOG = logging.getLogger('app.server')


class SocketDescriptor:
    """Дескриптор для атрибута порт"""
    def __init__(self):
        self._value = DEFAULT_PORT

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        if not 0 < value < 65536:
            LOG.warning(f'Не удалось подключиться к порту {value}')
            print(f'Указан неверный порт, используется порт по умолчанию: {DEFAULT_PORT}')
            raise ValueError('Порт должен быть целым неотрицательным числом')
        self._value = value
