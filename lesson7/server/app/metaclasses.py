from socket import socket, AF_INET, SOCK_STREAM
import dis
from server.app.descriptors import SocketDescriptor


class ServerSocket(socket):
    """Класс серверного сокета"""
    def __init__(self, AdressFamily=AF_INET, SocketKind=SOCK_STREAM):
        super().__init__(AdressFamily, SocketKind)
    port = SocketDescriptor()


class ServerVerifier(type):
    """Метакласс для проверки сервера"""
    def __init__(cls, clsname, bases, clsdict):
        for value in clsdict.values():
            if hasattr(value, '__call__'):
                if '(connect)' in dis.Bytecode(value).dis():
                    raise TypeError("Класс Server не должен содержать метод connect")
            if isinstance(value, socket):
                raise TypeError("Сокет не должен создаваться на уровне класса")
        if '(SOCK_STREAM)' not in dis.Bytecode(clsdict['__init__']).dis():
            raise ConnectionError("Сокет должен использовать TCP")

        type.__init__(cls, clsname, bases, clsdict)
