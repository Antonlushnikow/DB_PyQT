import argparse
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

from client_gui import MainWindow

base_dir = str(Path(__file__).parent.parent.resolve())
print(base_dir)
if base_dir not in sys.path:
    sys.path.append(base_dir)


from db_handlers import add_message, add_contact, get_contacts, get_last_messages, del_contact
from common.utils import get_message, send_message, send_encrypted_message, get_encrypted_message
from common.constants import DEFAULT_PORT, DEFAULT_HOST, ACTION, TIME, RESPONSE, TYPE, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, USER_LIST, CONTACT_LIST, CONTACT_NAME, PASSWD, SECRET_KEY, ENCODING
import logging

from app.decorators import log
from threading import Thread

import dis


LOG = logging.getLogger('app.client')


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


class Client(metaclass=ClientVerifier):
    def __init__(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.user_list = []
        self.connected = False
        self.name = 'guest'
        self.passwd = None
        self.inbox = []
        self.contacts = []
        self.presence_response = None

    @log
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
                   and msg[DESTINATION] == name:
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
                    # вывод списка пользователей
                    elif msg[RESPONSE] == '202' and USER_LIST in msg:
                        self.user_list = msg[USER_LIST]
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
    def create_msg_presence(self, account_name, passwd_hash):
        """
        Возвращает приветственное сообщение
        :param account_name:
        :return presence_msg:
        """
        presence_msg = {
            ACTION: 'presence',
            TIME: time(),
            TYPE: 'status',
            ACCOUNT_NAME: account_name,
            PASSWD: passwd_hash,
        }
        return presence_msg

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

    @log
    def create_msg_exit(self, account_name='guest'):
        """
        Возвращает сообщение об отключении
        :param account_name:
        :return exit_msg:
        """
        exit_msg = {
            ACTION: 'exit',
            TIME: time(),
            ACCOUNT_NAME: account_name
        }
        return exit_msg

    @log
    def create_gui_message(self, account_name, dst_name, msg_body):
        """
        Возвращает сформированное сообщение или завершает процесс
        :param account_name:
        :param msg_body:
        :param dst_name:
        :return msg:
        """

        msg = {
            ACTION: 'message',
            TIME: time(),
            ACCOUNT_NAME: account_name,
            MESSAGE: msg_body,
            DESTINATION: dst_name
        }
        add_message(account_name, dst_name, msg_body)
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
        self.presence_response = response[RESPONSE]
        if RESPONSE in response:
            if response[RESPONSE] == '200':
                LOG.info('Server has responded with status 200 - OK')
                print('Server has responded with status 200 - OK')
                return True
            elif response[RESPONSE] == '211':
                LOG.info('Server has responded with status 211 - Register is successful')
                print('Server has responded with status 211 - Register is successful')
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

    def send_gui_message(self, sock, name, dst, msg):
        try:
            send_encrypted_message(sock, self.create_gui_message(name, dst, msg))
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
        send_encrypted_message(self.client_socket, self.create_msg_list())

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

    def send_register_msg(self, login, passwd):
        try:
            send_encrypted_message(self.client_socket, self.create_register_message(login, passwd))
            resp = get_encrypted_message(self.client_socket)
            print(f'resp - {resp}')
        except:
            print(f'Соединение с сервером было разорвано')
            LOG.critical(f'Соединение с сервером было разорвано')
            sys.exit(1)
        else:
            self.check_response(resp)
                # # self.client_socket.shutdown(SHUT_RDWR)
                # # self.client_socket.close()
                # # self.client_socket = socket(AF_INET, SOCK_STREAM)
                # sleep(1)
                # sys.exit(1)

    def login(self):
        send_encrypted_message(self.client_socket, self.create_msg_presence(self.name, self.passwd))

        message = self.client_socket.recv(32)
        hash_ = hmac.new(SECRET_KEY, message, 'sha256')
        digest = hash_.digest()
        self.client_socket.send(digest)

        resp = get_encrypted_message(self.client_socket)
        print(f'resp - {resp}')
        if not self.check_response(resp):
            sleep(1)
            sys.exit(1)
        else:
            receiver = Thread(target=self.print_message, args=(self.client_socket, self.name))
            receiver.daemon = True
            receiver.start()

            while True:
                sleep(1)
                if receiver.is_alive():
                    continue
                break

    def padding_text(self, text):
        ''' Выравнивание сообщения до длины, кратной 16 байтам.
            В данном случае исходное сообщение дополняется пробелами.
        '''
        pad_len = (16 - len(text) % 16) % 16
        return text + b' ' * pad_len

    def _encrypt(self, plaintext: bytes, key=SECRET_KEY):
        """ Шифрование сообщения plaintext ключом key.
            Атрибут iv - вектор инициализации для алгоритма шифрования.
            Если не задается явно при создании объекта-шифра, генерируется случайно.
            Его следует добавить в качестве префикса к финальному шифру,
            чтобы была возможность правильно расшифровать сообщение.
        """
        cipher = AES.new(key, AES.MODE_CBC)
        ciphertext = cipher.iv + cipher.encrypt(plaintext)
        return ciphertext

    def _decrypt(self, ciphertext: bytes, key):
        """ Расшифровка шифра ciphertext ключом key.
            Вектор инициализации берется из исходного шифра.
            Его длина для большинства режимов шифрования всегда 16 байт.
            Расшифровываться будет оставшаяся часть шифра.
        """
        cipher = AES.new(key, AES.MODE_CBC, iv=ciphertext[:16])
        msg = cipher.decrypt(ciphertext[16:])
        return msg

    def launch(self):
        server_name, server_port = self.parse_arguments()
        LOG.info(f'Подключение к {server_name}:{server_port}')

        try:
            self.client_socket.connect((server_name, server_port))
            LOG.info(f'Connect to {server_name}:{server_port}')

            self.connected = True
        except ConnectionRefusedError:
            print('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
            self.presence_response = '503'
            sys.exit(1)


if __name__ == '__main__':
    c = Client()
    threading.Thread(target=c.launch, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow(c)
    window.show()

    sys.exit(app.exec_())
