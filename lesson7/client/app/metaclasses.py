import dis
from socket import socket


class ClientVerifier(type):
    """Метакласс для проверки клиента"""
    def __init__(cls, clsname, bases, clsdict):
        for value in clsdict.values():
            if hasattr(value, '__call__'):
                if '(accept)' in dis.Bytecode(value).dis():
                    raise TypeError("Класс Client не должен содержать метод accept")
                if '(listen)' in dis.Bytecode(value).dis():
                    raise TypeError("Класс Client не должен содержать метод listen")
            if isinstance(value, socket):
                raise TypeError("Сокет не должен создаваться на уровне класса")
        if '(SOCK_STREAM)' not in dis.Bytecode(clsdict['__init__']).dis():
            raise ConnectionError("Сокет должен использовать TCP")
        type.__init__(cls, clsname, bases, clsdict)
