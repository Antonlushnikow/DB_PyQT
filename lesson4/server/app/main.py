from pathlib import Path

from db_handlers import create_user, add_history, get_obj_by_login

import argparse
from socket import socket, AF_INET, SOCK_STREAM
import sys
from time import time

import select

base_dir = str(Path(__file__).parent.parent.resolve())
if base_dir not in sys.path:
    sys.path.append(base_dir)


from common.utils import get_message, send_message
from common.constants import DEFAULT_PORT, TIME, ACTION, RESPONSE, MAX_CONNECTIONS, USER_LIST, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, CONTACT_NAME
import logging

from app.decorators import log

import dis

from app.models import User, UserContact


LOG = logging.getLogger('app.server')




# def db_adduser(obj, addr):
#     """
#     Добавляет пользователя в БД, если пользователя в ней нет.
#     Регистрирует время входа пользователя в таблице user_history.
#     """
#     try:
#         with Session() as session:
#             session.add(obj)
#             session.commit()
#             session.refresh(obj)
#     except:
#         with Session() as session:
#             obj = session.query(User).filter_by(login=obj.login).first()
#     finally:
#         user_hist = UserHistory(obj.id, addr)
#         with Session() as session:
#             session.add(user_hist)
#             session.commit()
#
#
# def db_addcontact(obj):
#     """
#     Добавляет контакт пользователя в БД, если такой связки пользователь-контакт не существует.
#     """
#     try:
#         with Session() as session:
#             session.add(obj)
#             session.commit()
#             return True
#     except:
#         return False
#
#
# def db_delcontact(user_id, contact_id):
#     """
#     Удаляет контакт пользователя из БД, если такой связки пользователь-контакт не существует.
#     """
#     try:
#         with Session() as session:
#             session.query(UserContact).filter_by(user_id=user_id, contact_id=contact_id).delete()
#             session.commit()
#             return True
#     except:
#         return False
#
#
# def db_getcontacts(login):
#     """
#     Возвращает список контактов пользователя
#     """
#     contacts = []
#     try:
#         with Session() as session:
#             contacts = list(contact.contact_id for contact in session.query(UserContact).filter_by(user_id=login).all())
#     finally:
#         return contacts


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
    def process_client_message(self, sock, msg, msg_list, client_list, addr=''):
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
        :param addr:
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

                # регистрация пользователя в БД
                # user = User(msg[ACCOUNT_NAME])
                create_user(msg[ACCOUNT_NAME], '')
                user = get_obj_by_login(msg[ACCOUNT_NAME])
                add_history(user.id)
                # db_adduser(user, addr)

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
        # Обработка запроса списка контактов
        elif ACTION in msg and msg[ACTION] == 'get_contacts' and TIME in msg and ACCOUNT_NAME in msg:
            # send_message(sock, {RESPONSE: "202", CONTACT_LIST: db_getcontacts(msg[ACCOUNT_NAME])})
            return
        # Обработка запроса добавления в контакты
        elif ACTION in msg and msg[ACTION] == 'add_contact' and TIME in msg and ACCOUNT_NAME in msg and CONTACT_NAME in msg:
            # запись контакта в БД
            user_cont = UserContact(msg[ACCOUNT_NAME], msg[CONTACT_NAME])
            # if db_addcontact(user_cont):
            #     send_message(sock, {RESPONSE: "206", MESSAGE: "Успешно"})
            # else:
            #     send_message(sock, {RESPONSE: "406", MESSAGE: "Ошибка"})
            return
        # Обработка запроса добавления в контакты
        elif ACTION in msg and msg[ACTION] == 'del_contact' and TIME in msg and ACCOUNT_NAME in msg and CONTACT_NAME in msg:
            # удаление контакта из БД
            # if db_delcontact(msg[ACCOUNT_NAME], msg[CONTACT_NAME]):
            #     send_message(sock, {RESPONSE: "206", MESSAGE: "Успешно"})
            # else:
            #     send_message(sock, {RESPONSE: "406", MESSAGE: "Ошибка"})
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
                self.process_client_message(client_socket, get_message(client_socket), [], clients, addr[0])

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