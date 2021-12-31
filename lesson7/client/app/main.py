import argparse
import hashlib
import hmac
import threading
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from time import time, sleep
import sys

from Cryptodome.Cipher import AES
from PyQt5.QtWidgets import QApplication
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from metaclasses import ClientVerifier
from client_gui import MainWindow

from db_handlers import add_message, add_contact, get_contacts, get_last_messages, del_contact
from client.common.utils import get_message, send_message, send_encrypted_message, get_encrypted_message
from client.common.constants import DEFAULT_PORT, DEFAULT_HOST, ACTION, TIME, RESPONSE, TYPE, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, USER_LIST, CONTACT_LIST, CONTACT_NAME, PASSWD, SECRET_KEY, ENCODING, CONTACT
import logging

from client.app.decorators import log, login_required
from threading import Thread


LOG = logging.getLogger('app.client')
socket_lock = threading.Lock()


class Client(metaclass=ClientVerifier):
    def __init__(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.user_list = {}
        self.is_authenticated = False
        self.name = 'guest'
        self.passwd = None
        self.inbox = []
        self.contacts = []
        self.presence_response = None

    @log
    # @login_required
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
                if ACTION in msg and msg[ACTION] == 'message' and SENDER in msg and MESSAGE in msg \
                   and msg[CONTACT] == name:
                    LOG.debug(f'Got message from {msg[SENDER]}')
                    print(f'\nПолучено сообщение от пользователя {msg[SENDER]}:\n{msg[MESSAGE]}')
                    self.inbox.append((msg[SENDER], msg[MESSAGE]))
                    print('')
                # если пришел код 445 - пользователь-получатель не существует
                elif RESPONSE in msg:
                    if msg[RESPONSE] == '445':
                        LOG.info('Server has responded with status 445 - Destination user does not exist')
                        print('Ошибка: Получатель не найден')
                    # если пришел код 210 - пользователь уже существует
                    elif msg[RESPONSE] == '210':
                        LOG.info('Server has responded with status 210 - user already exists')
                        print('Инфо: Пользователь существует')
                    # если пришел код 212 - запрос хеша пароля
                    elif msg[RESPONSE] == '212':
                        self.hash_password(msg['salt'])
                        LOG.info('Server has responded with status 212 - Password request')
                        print('Инфо: Запрос хеша')
                    # вывод списка пользователей
                    elif msg[RESPONSE] == '202' and USER_LIST in msg:
                        self.user_list = msg[USER_LIST]
                        print(self.user_list)
                        # print(f'Список пользователей: {msg[USER_LIST]}')
                    # вывод списка контактов
                    elif msg[RESPONSE] == '202' and CONTACT_LIST in msg:
                        print(f'Список контактов: {msg[CONTACT_LIST]}')
                    elif msg[RESPONSE] == '444':
                        print('Логин занят, попробуйте другой')
                else:
                    LOG.warning(f'Got incorrect message')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError):
                LOG.critical(f'Соединение разорвано')
                break

    @log
    def hash_password(self, salt):
        passwd_hash = hashlib.pbkdf2_hmac('sha256', self.passwd.encode(ENCODING), self.name.encode(ENCODING), 100000)
        passwd = hashlib.pbkdf2_hmac('sha256', passwd_hash, salt.encode(ENCODING), 100000)
        reg_msg = {RESPONSE: '212', PASSWD: passwd}
        send_encrypted_message(self.client_socket, reg_msg)

    @log
    def create_msg_presence(self):
        """
        Возвращает приветственное сообщение
        :param account_name:
        :return presence_msg:
        """
        presence_msg = {
            ACTION: 'presence',
            TIME: time(),
            TYPE: 'status'
        }
        return presence_msg

    @log
    def create_msg_login(self, account_name):
        """
        Возвращает приветственное сообщение
        :param account_name:
        :return presence_msg:
        """
        login_msg = {
            ACTION: 'login',
            TIME: time(),
            TYPE: 'status',
            ACCOUNT_NAME: account_name,
        }
        return login_msg

    @log
    def create_msg_get_contacts(self, account_name):
        """
        Запрашивает список контактов
        :param account_name:
        :return get_contacts_msg:
        """
        get_contacts_msg = {
            ACTION: 'get_contacts',
            TIME: time(),
            ACCOUNT_NAME: account_name
        }
        return get_contacts_msg

    @log
    def create_msg_add_contact(self, account_name):
        """
        Создает сообщение для добавления контакта
        :param account_name:
        :return add_contact_msg:
        """
        contact_name = input('Введите имя контакта:\n')
        add_contact_msg = {
            ACTION: 'add_contact',
            TIME: time(),
            ACCOUNT_NAME: account_name,
            CONTACT_NAME: contact_name
        }
        return add_contact_msg

    @log
    def create_msg_del_contact(self, account_name):
        """
        Создает сообщение для удаления контакта
        :param account_name:
        :return add_contact_msg:
        """
        contact_name = input('Введите имя контакта:\n')
        del_contact_msg = {
            ACTION: 'del_contact',
            TIME: time(),
            ACCOUNT_NAME: account_name,
            CONTACT_NAME: contact_name
        }
        return del_contact_msg

    @log
    def create_msg_list(self, account_name='guest'):
        """
        Возвращает запрос списка пользователей
        :param account_name:
        :return list_msg:
        """
        list_msg = {
            ACTION: 'list',
            TIME: time(),
            ACCOUNT_NAME: account_name,
        }
        return list_msg
    #
    # @log
    # def create_msg_exit(self, account_name='guest'):
    #     """
    #     Возвращает сообщение об отключении
    #     :param account_name:
    #     :return exit_msg:
    #     """
    #     exit_msg = {
    #         ACTION: 'exit',
    #         TIME: time(),
    #         ACCOUNT_NAME: account_name
    #     }
    #     return exit_msg

    @log
    def create_gui_message(self, account_name, contact, dst_name, msg_body):
        """
        Возвращает сформированное сообщение или завершает процесс
        :param account_name:
        :param msg_body:
        :param dst_name:
        :param contact:

        :return msg:
        """

        msg = {
            ACTION: 'message',
            TIME: time(),
            ACCOUNT_NAME: account_name,
            CONTACT: contact,
            MESSAGE: msg_body,
            DESTINATION: dst_name
        }

        return msg

    @log
    def create_register_message(self, account_name, passwd):
        """
        Возвращает сформированное сообщение для регистрации
        :param account_name:
        :param passwd:
        :return msg:
        """
        msg = {
            ACTION: 'register',
            TIME: time(),
            ACCOUNT_NAME: account_name,
            PASSWD: passwd,
        }
        return msg

    @log
    def check_response(self, response):
        """
        Проверяет ответ на приветственное сообщение.
        Возвращает True в случае успешного подключения и False при ошибке
        :param response:
        """
        # self.presence_response = response[RESPONSE]
        if RESPONSE in response:
            if response[RESPONSE] == '200':
                LOG.info('Server has responded with status 200 - OK')
                print('Server has responded with status 200 - OK')
                return True
            elif response[RESPONSE] == '211':
                LOG.info('Server has responded with status 211 - Register is successful')
                print('Server has responded with status 211 - Register is successful')
                return True
            elif response[RESPONSE] == '212':
                # ответ сервера об авторизации
                LOG.info('Server has responded with status 212 - Password request')
                print('Server has responded with status 212 - Password request')
                return True
            elif response[RESPONSE] == '444':
                LOG.info('Server has responded with status 444 - Login is incorrect')
                print('Логин занят, попробуйте другой')
                return False
            elif response[RESPONSE] == '410':
                LOG.info('Server has responded with status 410 - Login is incorrect')
                print('Пользователя не существует')
                return False
            elif response[RESPONSE] == '420':
                LOG.info('Server has responded with status 410 - Password is incorrect')
                print('Неверный пароль')
                return False
            else:
                LOG.critical('Server has responded with error 400 - Bad Request')
                print('Server has responded with error 400 - Bad Request')
                return False
        raise ValueError

    @log
    # @login_required
    def send_gui_message(self, sock, name, contact, dst, msg):
        try:
            send_encrypted_message(sock, self.create_gui_message(name, contact, dst, msg))
            add_message(name, contact, msg)
        except:
            print(f'Соединение с сервером было разорвано')
            LOG.critical(f'Соединение с сервером было разорвано')
            sys.exit(1)

    @log
    def parse_arguments(self):
        """
        Обрабатывает аргументы запуска клиента.
        Возврашает параметры подключения
        :return server_name:
        :return server_port:
        :return client_name:
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default=DEFAULT_HOST)
        parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT)
        # parser.add_argument('-n', '--name', default=self.name)
        namespace = parser.parse_args(sys.argv[1:])
        server_name = namespace.addr
        server_port = namespace.port
        # client_name = namespace.name

        if not 1023 < server_port < 65536:
            LOG.warning(f'Не удалось подключиться к порту {server_port}')
            print(f'Указан неверный порт, используется порт по умолчанию: {DEFAULT_PORT}')
            server_port = DEFAULT_PORT

        return server_name, server_port

    def check_online_users(self):
        send_encrypted_message(self.client_socket, self.create_msg_list(self.name))

    @property
    def online_users(self):
        return self.user_list

    def add_contact_(self, user, contact):
        add_contact(user, contact)

    def get_contacts_(self, user):
        self.contacts = get_contacts(user)

    def del_contact_(self, contact):
        del_contact(self.name, contact)

    def get_last_messages_(self, contact):
        return get_last_messages(self.name, contact)

    def register(self, login, passwd):
        try:
            send_encrypted_message(self.client_socket, self.create_register_message(login, passwd))
            resp = get_encrypted_message(self.client_socket)
            self.presence_response = resp[RESPONSE]
            print(f'resp - {resp}')
        except:
            print(f'Соединение с сервером было разорвано')
            LOG.critical(f'Соединение с сервером было разорвано')
            sys.exit(1)
        else:
            self.check_response(resp)

    def login(self):
        send_encrypted_message(self.client_socket, self.create_msg_login(self.name))
        # send_encrypted_message(self.client_socket, self.create_msg_login(self.name, self.passwd))
        # если пришел код 212 - запрос хеша пароля
        msg = get_encrypted_message(self.client_socket)
        if msg[RESPONSE] == '212':
            self.hash_password(msg['salt'])
            LOG.info('Server has responded with status 212 - Password request')
            print('Инфо: Запрос хеша')
        # message = self.client_socket.recv(32)
        # message = get_encrypted_message(self.client_socket)
        # hash_ = hmac.new(SECRET_KEY, message, 'sha256')
        # digest = hash_.digest()
        # self.client_socket.send(digest)
        #
        # resp = get_encrypted_message(self.client_socket)
        # self.presence_response = resp[RESPONSE]
        print(f'resp - {msg}')
        # if not self.check_response(resp):
        #     sleep(1)
        #     sys.exit(1)
        if self.check_response(msg[RESPONSE]):
            self.is_authenticated = True
            threading.Thread(target=self.receive, daemon=True).start()

    def receive(self):
        receiver = Thread(target=self.print_message, args=(self.client_socket, self.name))
        receiver.daemon = True
        receiver.start()

        while True:
            sleep(1)
            if receiver.is_alive():
                continue
            break

    def launch(self):
        server_name, server_port = self.parse_arguments()
        LOG.info(f'Подключение к {server_name}:{server_port}')

        try:
            self.client_socket.connect((server_name, server_port))
            LOG.info(f'Connect to {server_name}:{server_port}')
            #
            send_encrypted_message(self.client_socket, self.create_msg_presence())
            resp = get_encrypted_message(self.client_socket)
            if not self.check_response(resp):
                sleep(1)
                sys.exit(1)

            self.connected = True

        except ConnectionRefusedError:
            print('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
            self.presence_response = '503'
            sys.exit(1)

    def stop(self):
        sys.exit(1)


if __name__ == '__main__':
    c = Client()
    threading.Thread(target=c.launch, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow(c)
    window.show()

    sys.exit(app.exec_())
