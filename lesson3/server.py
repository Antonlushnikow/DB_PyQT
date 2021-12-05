import argparse
from socket import socket, AF_INET, SOCK_STREAM
import sys
from time import time

import select

from common.utils import get_message, send_message
from common.constants import DEFAULT_PORT, TIME, ACTION, RESPONSE, MAX_CONNECTIONS, USER_LIST, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION
import logging
from project_logs.config import server_log_config
from decorators import log

import collections
import dis

from db import User, UserContact, UserHistory, Base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

LOG = logging.getLogger('app.server')

engine = create_engine('sqlite:///db.sqlite', echo=True)
Base.metadata.create_all(engine)


def db_commit(obj):
    Session = sessionmaker(engine)

    with Session() as session:
        session.add(obj)
        session.commit()


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


class Server(metaclass=ServerVerifier):
    def __init__(self):
        self.server_socket = ServerSocket(AF_INET, SOCK_STREAM)

    @log
    def process_client_message(self, sock, msg, msg_list, client_list):
        """
        Метод проверяет тип и корректность запроса.
        Для приветственного сообщения проверяет, не занят ли логин,
        если нет - добавляет пару сокет - логин в словарь клиентов.
        Для обычного сообщения, проверяет корректность и добавляет
        кортеж (отправитель, сообщение, получатель) в список сообщений.
        Для запроса пользователей отправляет словарь со списком пользователей.
        Ничего не возвращает.
        :param sock:
        :param msg:
        :param msg_list:
        :param client_list:
        :return:
        """
        # Обработка приветственного сообщения
        if ACTION in msg and msg[ACTION] == 'presence' and TIME in msg and ACCOUNT_NAME in msg:
            LOG.debug(f'{msg[ACCOUNT_NAME]}\'s message is correct')
            if msg[ACCOUNT_NAME] in client_list.keys():
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                send_message(sock, {RESPONSE: '444'})
            else:
                send_message(sock, {RESPONSE: '200'})
                client_list[msg[ACCOUNT_NAME]] = sock
                user = User(msg[ACCOUNT_NAME])
                db_commit(user)

            return
        # Обработка сообщения от пользователя
        elif ACTION in msg and msg[ACTION] == 'message' and TIME in msg and ACCOUNT_NAME in msg:
            if msg[DESTINATION] in client_list.keys():
                msg_list.append((msg[ACCOUNT_NAME], msg[MESSAGE], msg[DESTINATION]))
                LOG.debug(f'Got message {msg[MESSAGE]} from {msg[ACCOUNT_NAME]}')
            else:
                LOG.critical(f'{msg[DESTINATION]}\' does not exist')
                send_message(sock, {RESPONSE: '445'})
            return
        # Обработка запроса списка пользователей
        elif ACTION in msg and msg[ACTION] == 'list' and TIME in msg and ACCOUNT_NAME in msg:
            send_message(sock, {USER_LIST: list(client_list.keys())})
            return
        # Обработка сообщения о выходе пользователя
        elif ACTION in msg and msg[ACTION] == 'exit' and TIME in msg and ACCOUNT_NAME in msg:
            if msg[ACCOUNT_NAME] in client_list.keys():
                del client_list[msg[ACCOUNT_NAME]]
                LOG.info(f'{msg[ACCOUNT_NAME]} has disconnected')
            return
        else:
            LOG.critical(f'{msg[ACCOUNT_NAME]}\'s message is incorrect')
            LOG.debug(f'{msg}')
            send_message(sock, {RESPONSE: '400'})
            return

    @log
    def parse_arguments(self):
        """
        Метод парсит аргументы запуска сервера и проверяет их корректность.
        Возвращает прослушиваемый адрес и порт.
        Если аргументы не заданы, возвращает значения по умолчанию.
        :return listen_name, listen_port:
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default='')
        parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT)
        namespace = parser.parse_args(sys.argv[1:])
        listen_name = namespace.addr
        self.server_socket.port = namespace.port

        # if not 1023 < listen_port < 65536:
        #     LOG.warning(f'Не удалось подключиться к порту {listen_port}')
        #     print(f'Указан неверный порт, используется порт по умолчанию: {DEFAULT_PORT}')
        #     listen_port = DEFAULT_PORT

        return listen_name

    def run(self):
        listen_name = self.parse_arguments()
        clients = {}  # словарь {логин: сокет, }
        messages = []  # список кортежей [(отправитель, сообщение, получатель), ]

        try:
            self.server_socket.bind((listen_name, self.server_socket.port))
        except OSError:
            print(f'Cannot bind to {listen_name}:{self.server_socket.port}. Switching to default params')
            LOG.critical(f'Cannot bind to {listen_name}:{self.server_socket.port}')
            self.server_socket.bind(('', self.server_socket.port))
        finally:
            self.server_socket.settimeout(0.5)

        self.server_socket.listen(MAX_CONNECTIONS)
        LOG.info(f'Listen {listen_name}:{self.server_socket.port}')
        print(f'Server has started.\nListen {listen_name}:{self.server_socket.port}')

        while True:
            try:
                client_socket, addr = self.server_socket.accept()
            except OSError:
                pass
            else:
                print(f'Host {addr} has connected')
                LOG.info(f'Host {addr} has connected')



                # Получение приветственного сообщения
                self.process_client_message(client_socket, get_message(client_socket), [], clients)

            hosts_who_send, hosts_who_listen = [], []

            try:
                if clients:
                    hosts_who_send, hosts_who_listen, _ = select.select(clients.values(), clients.values(), [], 0)
            except OSError:
                pass

            if hosts_who_send:
                for host in hosts_who_send:
                    try:
                        self.process_client_message(host, get_message(host), messages, clients)
                    except:
                        LOG.info(f'{host} disconnected from the server')

                        # удаление отключенного пользователя из словаря
                        key_host = ''
                        for key, value in clients.items():
                            if value == host:
                                key_host = key
                        if key_host:
                            del clients[key_host]

            for message in messages:
                msg = {
                    ACTION: MESSAGE,
                    SENDER: message[0],
                    TIME: time(),
                    MESSAGE: message[1],
                    DESTINATION: message[2]
                }
                LOG.info(f'Отправка сообщения пользователю {msg[DESTINATION]}')
                send_message(clients[msg[DESTINATION]], msg)
            messages.clear()


def main():
    srv = Server()
    srv.run()


if __name__ == '__main__':
    main()
