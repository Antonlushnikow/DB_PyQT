import select
import os
import logging
import sys
from fastapi import FastAPI
from base64 import b64encode
from socket import AF_INET, SOCK_STREAM
from time import time
from PyQt5.QtWidgets import QApplication
from common.utils import send_encrypted_message, get_encrypted_message
from common.constants import DEFAULT_PORT, TIME, ACTION, RESPONSE, \
    MAX_CONNECTIONS, USER_LIST, ACCOUNT_NAME, MESSAGE, SENDER, DESTINATION, \
    CONTACT_NAME, CONTACT_LIST, PASSWD, ENCODING, CONTACT, SALT
from app.decorators import log
from app.metaclasses import ServerSocket, ServerVerifier
from app.server_gui import ServerGUI
from app.api.api_v1.api import api_router
from app.db_handlers import create_user, add_history, get_obj_by_login, \
    add_contact, delete_contact, get_contacts
from project_logs.config import server_log_config


app = FastAPI(title='Messenger', openapi_url='/127.0.0.1/api/v1/openapi.json')
app.include_router(api_router, prefix="/api/v1")


SECRET_KEY = b'super_secret_key'
LOG = logging.getLogger('app.server')


class Server(metaclass=ServerVerifier):
    """
    Основной класс сервера
    """
    def __init__(self, addr='', port=DEFAULT_PORT):
        self.addr = addr
        self.port = int(port)
        self.server_socket = ServerSocket(AF_INET, SOCK_STREAM)
        self.client_sockets = {}
        self.active_clients = {}

    @log
    def process_client_message(self, sock, msg, msg_list):
        """
        Метод проверяет тип входящего сообщения, проверяет корректность сообщения
        и отправляет соответствующий ответ клиенту
        """
        resp = {RESPONSE: ''}
        # Обработка приветственного сообщения
        if ACTION in msg and msg[ACTION] == 'presence' and TIME in msg:
            send_encrypted_message(sock, {RESPONSE: '200'})
            self.client_sockets[sock.getpeername()[0]+str(sock.getpeername()[1])] = sock
            return
        # Обработка сообщения о регистрации
        elif ACTION in msg and msg[ACTION] == 'register' and TIME in msg and ACCOUNT_NAME in msg:
            user = get_obj_by_login(msg[ACCOUNT_NAME])
            if not user:
                # Пользователь не существует
                passwd, salt = self.create_password_hash(sock)
                create_user(msg[ACCOUNT_NAME], passwd, salt, '')
                send_encrypted_message(sock, {RESPONSE: '211'})
            else:
                # Пользователь существует
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                send_encrypted_message(sock, {RESPONSE: '444'})
            return
        # Обработка авторизации
        if ACTION in msg and msg[ACTION] == 'login' and TIME in msg and ACCOUNT_NAME in msg:
            LOG.debug(f'{msg[ACCOUNT_NAME]}\'s message is correct')
            if msg[ACCOUNT_NAME] in self.active_clients.values():
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                resp = {RESPONSE: '444'}
            else:
                # проверка существования пользователя
                user = get_obj_by_login(msg[ACCOUNT_NAME])
                if user:
                    if self.check_password(sock, user):
                        # пароль верный
                        add_history(user.id)
                        resp = {RESPONSE: '200'}
                        self.active_clients[sock.getpeername()[0]+str(sock.getpeername()[1])] = msg[ACCOUNT_NAME]
                    else:
                        # неправильный пароль
                        resp = {RESPONSE: '420'}
                else:
                    # пользователь не существует
                    resp = {RESPONSE: '410'}
            send_encrypted_message(sock, resp)
            return
        # Обработка сообщения от пользователя
        elif ACTION in msg and msg[ACTION] == 'message' and TIME in msg and ACCOUNT_NAME in msg:
            if msg[DESTINATION] in self.client_sockets.keys():
                msg_list.append((msg[ACCOUNT_NAME], msg[MESSAGE], msg[DESTINATION], msg[CONTACT]))
                LOG.debug(f'Got message {msg[MESSAGE]} from {msg[ACCOUNT_NAME]}')
            else:
                LOG.critical(f'{msg[DESTINATION]}\' does not exist')
                send_encrypted_message(sock, {RESPONSE: '445'})
            return
        # Обработка запроса списка пользователей онлайн
        elif ACTION in msg and msg[ACTION] == 'list' and TIME in msg and ACCOUNT_NAME in msg:
            print(f'msg22 - {msg}')
            send_encrypted_message(sock, {RESPONSE: '202', USER_LIST: self.online_users})
            return
        # Обработка запроса списка контактов
        elif ACTION in msg and msg[ACTION] == 'get_contacts' and ACCOUNT_NAME in msg:
            user_id = get_obj_by_login(msg[ACCOUNT_NAME]).id
            contacts = list(contact.login for contact in get_contacts(user_id)) or []
            send_encrypted_message(sock, {RESPONSE: '203', CONTACT_LIST: contacts})
            return
        # Обработка запроса добавления в контакты
        elif ACTION in msg and msg[ACTION] == 'add_contact' and ACCOUNT_NAME in msg and CONTACT_NAME in msg:
            # запись контакта в БД
            try:
                user_id = get_obj_by_login(msg[ACCOUNT_NAME]).id
                contact_id = get_obj_by_login(msg[CONTACT_NAME]).id
            except:
                send_encrypted_message(sock, {RESPONSE: "406", MESSAGE: "Ошибка"})
            else:
                add_contact(user_id, contact_id)
                contacts = list(contact.login for contact in get_contacts(user_id)) or []
                send_encrypted_message(sock, {RESPONSE: "206", MESSAGE: "Успешно", CONTACT_LIST: contacts})

            return
        # Обработка запроса удаления из контактов
        elif ACTION in msg and msg[ACTION] == 'del_contact' and ACCOUNT_NAME in msg and CONTACT_NAME in msg:
            try:
                user_id = get_obj_by_login(msg[ACCOUNT_NAME]).id
                contact_id = get_obj_by_login(msg[CONTACT_NAME]).id
            except:
                send_encrypted_message(sock, {RESPONSE: "406", MESSAGE: "Ошибка"})
            else:
                delete_contact(user_id, contact_id)
                contacts = list(contact.login for contact in get_contacts(user_id)) or []
                send_encrypted_message(sock, {RESPONSE: "207", MESSAGE: "Успешно", CONTACT_LIST: contacts})
            return
        # Получено некорректное сообщение
        else:
            LOG.critical(f'{msg[ACCOUNT_NAME]}\'s message is incorrect')
            LOG.debug(f'{msg}')
            send_encrypted_message(sock, {RESPONSE: '400'})
            return

    @log
    def create_password_hash(self, sock):
        """
        Отправляет пользователю соль
        Принимает получившийся хеш пароля
        Возвращает соль и хеш
        """
        random_string = os.urandom(32)
        salt = b64encode(random_string).decode(ENCODING)
        msg = {SALT: salt}

        send_encrypted_message(sock, msg)
        resp = get_encrypted_message(sock)

        passwd_hash = resp[PASSWD]

        return passwd_hash, salt

    def check_password(self, sock, user):
        """
        Проверка пароля пользователя. Отправляет клиенту соль,
        получает ответ, сравнивает хеши
        """
        login_msg = {RESPONSE: '212', SALT: user.salt}
        send_encrypted_message(sock, login_msg)
        ans = get_encrypted_message(sock)
        return ans[PASSWD] == user.password_hash

    @property
    def online_users(self):
        """
        Возврашает словарь с пользователями онлайн
        """
        online_dict = {}
        for key, value in self.active_clients.items():
            online_dict[value] = key
        return online_dict

    @log
    def run(self):
        """Запуск сервера"""
        messages = []

        try:
            self.server_socket.bind((self.addr, self.port))
        except OSError:
            print(f'Cannot bind to {self.addr}:{self.port}. Switching to default params')
            LOG.critical(f'Cannot bind to {self.addr}:{self.port}')
            self.server_socket.bind(('', self.port))
        finally:
            self.server_socket.settimeout(0.5)

        self.server_socket.listen(MAX_CONNECTIONS)
        LOG.info(f'Listen {self.addr}:{self.port}')
        print(f'Server has started.\nListen {self.addr}:{self.port}')

        while True:
            try:
                client_socket, addr = self.server_socket.accept()
            except OSError:
                pass
            else:
                print(f'Host {addr} has connected')
                LOG.info(f'Host {addr} has connected')

                # Получение приветственного сообщения
                self.process_client_message(client_socket, get_encrypted_message(client_socket), [])

            hosts_who_send, hosts_who_listen = [], []

            try:
                if self.client_sockets:
                    hosts_who_send, hosts_who_listen, _ = select.select(self.client_sockets.values(), self.client_sockets.values(), [], 0)
                    print(f'{self.active_clients}')
                    # print(f'hosts_who_listen: {hosts_who_listen}')
            except OSError:
                pass

            if hosts_who_send:
                for host in hosts_who_send:
                    try:
                        self.process_client_message(host, get_encrypted_message(host), messages)
                    except:
                        LOG.info(f'{host} disconnected from the server')
                        print(f'{host} disconnected from the server')

                        # удаление отключенного пользователя из словаря
                        key_host = ''
                        for key, value in self.client_sockets.items():
                            if value == host:
                                key_host = key
                        if key_host:
                            del self.client_sockets[key_host]
                            if key_host in self.active_clients.keys():
                                del self.active_clients[key_host]

            for message in messages:
                msg = {
                    ACTION: MESSAGE,
                    SENDER: message[0],
                    TIME: time(),
                    MESSAGE: message[1],
                    DESTINATION: message[2],
                    CONTACT: message[3],
                }
                LOG.info(f'Отправка сообщения пользователю {msg[DESTINATION]}')

                send_encrypted_message(self.client_sockets[msg[DESTINATION]], msg)
            messages.clear()


if __name__ == '__main__':
    # создание экземпляра класса и основного окна сервера
    srv = Server()
    app = QApplication(sys.argv)
    window = ServerGUI(srv)
    window.show()
    sys.exit(app.exec_())
