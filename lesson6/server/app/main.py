import os
import threading
from datetime import datetime
from pathlib import Path

from db_handlers import create_user, add_history, get_obj_by_login, add_contact, delete_contact, get_contacts

import argparse
from socket import socket, AF_INET, SOCK_STREAM
import sys
from time import time

from PyQt5.QtWidgets import QMainWindow, QApplication
import server_form
import select

base_dir = str(Path(__file__).parent.parent.resolve())
if base_dir not in sys.path:
    sys.path.append(base_dir)

from common.utils import send_encrypted_message, get_encrypted_message
from common.constants import DEFAULT_PORT, TIME, ACTION, RESPONSE, MAX_CONNECTIONS, USER_LIST, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, CONTACT_NAME, CONTACT_LIST, PASSWD, SECRET_KEY
import logging

from app.decorators import log

import dis
import hmac


LOG = logging.getLogger('app.server')

online_users = []


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
    def __init__(self, addr='', port=DEFAULT_PORT):
        self.addr = addr
        self.port = int(port)
        self.server_socket = ServerSocket(AF_INET, SOCK_STREAM)
        self.clients = {}  # словарь {логин: сокет, }
        self.active_clients = {}

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
        if ACTION in msg and msg[ACTION] == 'presence' and TIME in msg and ACCOUNT_NAME in msg and PASSWD in msg:
            LOG.debug(f'{msg[ACCOUNT_NAME]}\'s message is correct')
            if msg[ACCOUNT_NAME] in client_list.keys():
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                send_encrypted_message(sock, {RESPONSE: '444'})
            else:
                # проверка существования пользователя
                if self.server_authenticate(sock):
                    user = get_obj_by_login(msg[ACCOUNT_NAME])
                    if user:
                        if self.check_credentials(user, msg[PASSWD]):
                            add_history(user.id)
                            send_encrypted_message(sock, {RESPONSE: '200'})
                        else:
                            send_encrypted_message(sock, {RESPONSE: '420'})  # неправильный пароль
                            return
                    else:
                        send_encrypted_message(sock, {RESPONSE: '410'})  # пользователь не существует
                        return
                    client_list[msg[ACCOUNT_NAME]] = sock
                    self.active_clients[msg[ACCOUNT_NAME]] = (client_list[msg[ACCOUNT_NAME]].getpeername()[0], datetime.now())
            return
        # Обработка сообщения от пользователя
        elif ACTION in msg and msg[ACTION] == 'message' and TIME in msg and ACCOUNT_NAME in msg:
            if msg[DESTINATION] in client_list.keys():
                msg_list.append((msg[ACCOUNT_NAME], msg[MESSAGE], msg[DESTINATION]))
                LOG.debug(f'Got message {msg[MESSAGE]} from {msg[ACCOUNT_NAME]}')
            else:
                LOG.critical(f'{msg[DESTINATION]}\' does not exist')
                send_encrypted_message(sock, {RESPONSE: '445'})
            return
        # Обработка сообщения о регистрации
        elif ACTION in msg and msg[ACTION] == 'register' and TIME in msg and ACCOUNT_NAME in msg and PASSWD in msg:
            user = get_obj_by_login(msg[ACCOUNT_NAME])
            if not user:
                create_user(msg[ACCOUNT_NAME], msg[PASSWD], '')
                send_encrypted_message(sock, {RESPONSE: '211'})
            else:
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                send_encrypted_message(sock, {RESPONSE: '444'})
            return
        # Обработка запроса списка пользователей онлайн
        elif ACTION in msg and msg[ACTION] == 'list' and TIME in msg and ACCOUNT_NAME in msg:
            send_encrypted_message(sock, {RESPONSE: "202", USER_LIST: list(client_list.keys())})
            return
        # Обработка запроса списка контактов
        elif ACTION in msg and msg[ACTION] == 'get_contacts' and TIME in msg and ACCOUNT_NAME in msg:
            user_id = get_obj_by_login(msg[ACCOUNT_NAME]).id
            contacts = list(contact.login for contact in get_contacts(user_id)) or []
            send_encrypted_message(sock, {RESPONSE: '202', CONTACT_LIST: contacts})
            return
        # Обработка запроса добавления в контакты
        elif ACTION in msg and msg[ACTION] == 'add_contact' and TIME in msg and ACCOUNT_NAME in msg and CONTACT_NAME in msg:
            # запись контакта в БД
            try:
                user_id = get_obj_by_login(msg[ACCOUNT_NAME]).id
                contact_id = get_obj_by_login(msg[CONTACT_NAME]).id
            except:
                send_encrypted_message(sock, {RESPONSE: "406", MESSAGE: "Ошибка"})
            else:
                add_contact(user_id, contact_id)
                send_encrypted_message(sock, {RESPONSE: "206", MESSAGE: "Успешно"})

            return
        # Обработка запроса удаления из контактов
        elif ACTION in msg and msg[ACTION] == 'del_contact' and TIME in msg and ACCOUNT_NAME in msg and CONTACT_NAME in msg:
            try:
                user_id = get_obj_by_login(msg[ACCOUNT_NAME]).id
                contact_id = get_obj_by_login(msg[CONTACT_NAME]).id
            except:
                send_encrypted_message(sock, {RESPONSE: "406", MESSAGE: "Ошибка"})
            else:
                delete_contact(user_id, contact_id)
                send_encrypted_message(sock, {RESPONSE: "206", MESSAGE: "Успешно"})
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
            send_encrypted_message(sock, {RESPONSE: '400'})
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
        parser.add_argument('-a', '--addr', default=self.addr)
        parser.add_argument('-p', '--port', type=int, default=self.port)
        namespace = parser.parse_args(sys.argv[1:])
        listen_name = namespace.addr
        self.server_socket.port = namespace.port

        return listen_name

    def check_credentials(self, user, passwd):
        if user.password_hash == passwd:
            return True
        return False

    @property
    def online_users(self):
        return list(self.clients.keys())

    def server_authenticate(self, sock):
        message = os.urandom(32)
        sock.send(message)

        hash = hmac.new(SECRET_KEY, message, 'sha256')
        digest = hash.digest()

        response = sock.recv(len(digest))
        return hmac.compare_digest(digest, response)

    def run(self):
        # global online_users
        listen_name = self.parse_arguments()

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
            # print(self.clients.keys())
            try:
                client_socket, addr = self.server_socket.accept()
            except OSError:
                pass
            else:
                print(f'Host {addr} has connected')
                LOG.info(f'Host {addr} has connected')

                # Получение приветственного сообщения
                self.process_client_message(client_socket, get_encrypted_message(client_socket), [], self.clients, addr[0])

            hosts_who_send, hosts_who_listen = [], []

            try:
                if self.clients:
                    hosts_who_send, hosts_who_listen, _ = select.select(self.clients.values(), self.clients.values(), [], 0)
                    # print(f'hosts_who_send: {hosts_who_send}')
                    # print(f'hosts_who_listen: {hosts_who_listen}')
            except OSError:
                pass

            if hosts_who_send:
                for host in hosts_who_send:
                    try:
                        self.process_client_message(host, get_encrypted_message(host), messages, self.clients)
                    except:
                        LOG.info(f'{host} disconnected from the server')
                        print(f'{host} disconnected from the server')

                        # удаление отключенного пользователя из словаря
                        key_host = ''
                        for key, value in self.clients.items():
                            if value == host:
                                key_host = key
                        if key_host:
                            del self.clients[key_host]
                            del self.active_clients[key_host]

            for message in messages:
                msg = {
                    ACTION: MESSAGE,
                    SENDER: message[0],
                    TIME: time(),
                    MESSAGE: message[1],
                    DESTINATION: message[2]
                }
                print(msg)
                LOG.info(f'Отправка сообщения пользователю {msg[DESTINATION]}')

                send_encrypted_message(self.clients[msg[DESTINATION]], msg)
            messages.clear()


if __name__ == '__main__':
    srv = Server()
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = server_form.Ui_Dialog()
    ui.setupUi(window)
    ui.label_3.setText(''.join(online_users))
    ui.pushButton.clicked.connect(lambda: thread(ui.lineEdit.text(), ui.lineEdit_2.text()))

    def refresh_online_users():
        ui.tableView.setModel(server_form.gui_create_model(srv))

    ui.refreshButton.clicked.connect(refresh_online_users)
    ui.tableView.setModel(server_form.gui_create_model(srv))

    window.show()

    def get_online_users():
        ui.label_3.setText('\n'.join(srv.online_users))

    def thread(addr, port):
        ui.label_4.setText('Connected')
        ui.pushButton.setDisabled(True)
        threading.Thread(target=start, args=(addr, port), daemon=True).start()


    def start(addr, port):
        srv.addr = addr
        srv.port = port
        srv.run()

    sys.exit(app.exec_())
