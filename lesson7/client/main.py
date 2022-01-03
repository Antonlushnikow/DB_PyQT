import argparse
import hashlib
import threading
import sys
import logging

from socket import socket, AF_INET, SOCK_STREAM
from time import time, sleep
from base64 import b64encode
from threading import Thread
from PyQt5.QtWidgets import QApplication

from app.metaclasses import ClientVerifier
from app.client_gui import StartWindow
from app.db_handlers import add_message, add_contact, get_contacts, get_last_messages, \
    del_contact, delete_contacts
from common.utils import send_encrypted_message, get_encrypted_message
from common.constants import DEFAULT_PORT, DEFAULT_HOST, ACTION, TIME, RESPONSE, TYPE, \
    ACCOUNT_NAME, MESSAGE, SENDER, DESTINATION, USER_LIST, CONTACT_LIST, CONTACT_NAME, PASSWD, \
    ENCODING, CONTACT, SALT
from app.decorators import log, login_required
from project_logs.config import client_log_config


SECRET_KEY = b'super_secret_key'
LOG = logging.getLogger('app.client')
socket_lock = threading.Lock()


class Client(metaclass=ClientVerifier):
    """Основной класс клиента"""
    def __init__(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.connected = False
        self.is_authenticated = False
        self.name = 'guest'
        self.passwd = None
        self.inbox = []
        self.user_list = {}
        self.contacts = []
        self.presence_response = None

    @log
    @login_required
    def print_message(self, sock, name):
        """
        Принимает и проверяет сообщения от сервера.
        Ничего не возвращает
        :param sock:
        :param name:
        :return:
        """
        while True:
            try:
                msg = get_encrypted_message(sock)
                # если пришло сообщение
                if ACTION in msg and msg[ACTION] == 'message' and SENDER in msg and MESSAGE in msg \
                   and msg[CONTACT] == name:
                    LOG.debug(f'Got message from {msg[SENDER]}')
                    print(f'\nПолучено сообщение от пользователя {msg[SENDER]}:\n{msg[MESSAGE]}')
                    self.inbox.append((msg[SENDER], msg[MESSAGE]))
                # если пришел код 445 - пользователь-получатель не существует
                elif RESPONSE in msg:
                    if msg[RESPONSE] == '445':
                        LOG.info('Server has responded with status 445 - Destination user does not exist')
                        print('Ошибка: Получатель не найден')
                    # если пришел код 210 - пользователь уже существует
                    elif msg[RESPONSE] == '210':
                        LOG.info('Server has responded with status 210 - user already exists')
                        print('Инфо: Пользователь существует')
                    elif msg[RESPONSE] == '410':
                        LOG.info('Server has responded with status 410 - Login is incorrect')
                        print('Пользователя не существует')
                    # # если пришел код 212 - запрос хеша пароля
                    # elif msg[RESPONSE] == '212':
                    #     self.hash_password(msg['salt'])
                    #     LOG.info('Server has responded with status 212 - Password request')
                    #     print('Инфо: Запрос хеша')
                    # вывод списка пользователей
                    elif msg[RESPONSE] == '202' and USER_LIST in msg:
                        self.user_list = msg[USER_LIST]
                        print(self.user_list)
                        # print(f'Список пользователей: {msg[USER_LIST]}')
                    # вывод списка контактов
                    elif msg[RESPONSE] == '203' and CONTACT_LIST in msg:
                        print(f'Список контактов: {msg[CONTACT_LIST]}')
                        self.contacts = msg[CONTACT_LIST]
                    # вывод добавления контактов
                    elif msg[RESPONSE] == '206':
                        print(f'Контакт добавлен')
                        self.contacts = msg[CONTACT_LIST]
                    # вывод удаления контактов
                    elif msg[RESPONSE] == '207':
                        print(f'Контакт удален')
                        self.contacts = msg[CONTACT_LIST]
                    elif msg[RESPONSE] == '444':
                        print('Логин занят, попробуйте другой')
                else:
                    LOG.warning(f'Got incorrect message')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError):
                LOG.critical(f'Соединение разорвано')
                break

    @log
    def parse_arguments(self):
        """
        Обрабатывает аргументы запуска клиента.
        Возврашает параметры подключения
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default=DEFAULT_HOST)
        parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT)
        namespace = parser.parse_args(sys.argv[1:])
        server_name = namespace.addr
        server_port = namespace.port

        if not 1023 < server_port < 65536:
            LOG.warning(f'Не удалось подключиться к порту {server_port}')
            print(f'Указан неверный порт, используется порт по умолчанию: {DEFAULT_PORT}')
            server_port = DEFAULT_PORT

        return server_name, server_port

    def check_online_users(self):
        msg = {
            ACTION: 'list',
            TIME: time(),
            ACCOUNT_NAME: self.name,
        }
        send_encrypted_message(self.client_socket, msg)

    @property
    def online_users(self):
        """Возвращает словарь с подключенными пользователями"""
        return self.user_list

    def add_contact_(self, contact):
        """Добавляет контакты в локальную и серверную БД"""
        msg = {
            ACTION: 'add_contact',
            ACCOUNT_NAME: self.name,
            CONTACT_NAME: contact
        }

        send_encrypted_message(self.client_socket, msg)

        add_contact(self.name, contact)

    def get_contacts_(self, user):
        """
        Отправляет запрос на обновление списка контактов
        """
        delete_contacts(user)
        msg = {
            ACTION: 'get_contacts',
            ACCOUNT_NAME: user
        }
        send_encrypted_message(self.client_socket, msg)

    def del_contact_(self, contact):
        """Удаляет контакт из локальной и серверной БД"""
        msg = {
            ACTION: 'del_contact',
            ACCOUNT_NAME: self.name,
            CONTACT_NAME: contact
        }
        # with socket_lock:
        send_encrypted_message(self.client_socket, msg)
        del_contact(self.name, contact)

    def get_last_messages_(self, contact):
        """Возвращает последние пять сообщений"""
        return get_last_messages(self.name, contact)

    def register(self, login, passwd):
        """
        Отправляет запрос о регистрации
        Получает соль
        Генерирует и отправляет хэш пароля
        """
        try:
            msg = {
                ACTION: 'register',
                TIME: time(),
                ACCOUNT_NAME: login,
            }

            send_encrypted_message(self.client_socket, msg)
            resp = get_encrypted_message(self.client_socket)

            salt = resp[SALT]
            passwd_hash = hashlib.pbkdf2_hmac('sha256', passwd.encode(ENCODING), salt.encode(ENCODING), 100000)

            passwd_hash = b64encode(passwd_hash).decode(ENCODING)

            msg = {
                PASSWD: passwd_hash
            }

            send_encrypted_message(self.client_socket, msg)
            resp = get_encrypted_message(self.client_socket)

            self.presence_response = resp[RESPONSE]
            print(f'resp - {resp}')
        except:
            print(f'Соединение с сервером было разорвано')
            LOG.critical(f'Соединение с сервером было разорвано')
            sys.exit(1)

    def login(self):
        """
        Отправка аутентификационных данных
        Получение ответа от сервера
        В случае успеха - запуск чата
        """
        msg = {
            ACTION: 'login',
            TIME: time(),
            ACCOUNT_NAME: self.name,
        }

        send_encrypted_message(self.client_socket, msg)
        resp = get_encrypted_message(self.client_socket)
        if resp[RESPONSE] == '212':
            salt = resp[SALT]

            passwd_hash = hashlib.pbkdf2_hmac('sha256', self.passwd.encode(ENCODING), salt.encode(ENCODING), 100000)
            passwd_hash = b64encode(passwd_hash).decode(ENCODING)

            msg = {
                PASSWD: passwd_hash
            }

            send_encrypted_message(self.client_socket, msg)
            resp = get_encrypted_message(self.client_socket)

            self.presence_response = resp[RESPONSE]
            print(f'resp - {resp}')

            if self.presence_response == '200':
                self.is_authenticated = True
                threading.Thread(target=self.receive, daemon=True).start()
        else:
            self.presence_response = resp[RESPONSE]

    @log
    def hash_password(self, salt):
        """Генерирует и отправляет хеш пароля"""
        passwd_hash = hashlib.pbkdf2_hmac('sha256', self.passwd.encode(ENCODING), self.name.encode(ENCODING), 100000)
        passwd = hashlib.pbkdf2_hmac('sha256', passwd_hash, salt.encode(ENCODING), 100000)
        reg_msg = {RESPONSE: '212', PASSWD: passwd}
        send_encrypted_message(self.client_socket, reg_msg)

    @log
    @login_required
    def send_message(self, sock, name, contact, dst, msg):
        """Отправляет сообщение пользователю"""
        try:
            msg_ = {
                ACTION: 'message',
                TIME: time(),
                ACCOUNT_NAME: name,
                CONTACT: contact,
                MESSAGE: msg,
                DESTINATION: dst
            }
            send_encrypted_message(sock, msg_)
            add_message(name, contact, msg)
        except:
            print(f'Соединение с сервером было разорвано')
            LOG.critical(f'Соединение с сервером было разорвано')
            sys.exit(1)

    def receive(self):
        """Запускает поток приема сообщений"""
        receiver = Thread(target=self.print_message, args=(self.client_socket, self.name))
        receiver.daemon = True
        receiver.start()

        while True:
            sleep(1)
            if receiver.is_alive():
                continue
            break

    def launch(self):
        """Запуск клиента, подключение к серверу"""
        server_name, server_port = self.parse_arguments()
        LOG.info(f'Подключение к {server_name}:{server_port}')

        try:
            self.client_socket.connect((server_name, server_port))
            LOG.info(f'Connect to {server_name}:{server_port}')
            #
            presence_msg = {
                ACTION: 'presence',
                TIME: time(),
                TYPE: 'status'
            }
            send_encrypted_message(self.client_socket, presence_msg)
            resp = get_encrypted_message(self.client_socket)
            if resp[RESPONSE] != '200':
                sleep(1)
                sys.exit(1)
            self.connected = True

        except ConnectionRefusedError:
            print('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
            self.presence_response = '503'
            sys.exit(1)

    def stop(self):
        """Остановка приложения"""
        sys.exit(1)


if __name__ == '__main__':
    c = Client()
    app = QApplication(sys.argv)
    window = StartWindow(c)
    window.show()
    sys.exit(app.exec_())
