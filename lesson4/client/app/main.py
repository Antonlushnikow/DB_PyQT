import argparse
from socket import socket, AF_INET, SOCK_STREAM
from time import time, sleep
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.utils import get_message, send_message
from common.constants import DEFAULT_PORT, DEFAULT_HOST, ACTION, TIME, RESPONSE, TYPE, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, USER_LIST, CONTACT_LIST, CONTACT_NAME
import logging

from app.decorators import log
from threading import Thread

import dis

from models import Base

LOG = logging.getLogger('app.client')


# Создание БД
engine = create_engine('sqlite:///db_client.sqlite', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(engine)


def db_adduser(obj):
    """
    Добавляет пользователя в БД, если пользователя в ней нет.
    Регистрирует время входа пользователя в таблице user_history.
    """
    try:
        with Session() as session:
            session.add(obj)
            session.commit()
    except:
        pass


def db_addmessage(obj):
    """
    Добавляет пользователя в БД, если пользователя в ней нет.
    Регистрирует время входа пользователя в таблице user_history.
    """
    try:
        with Session() as session:
            session.add(obj)
            session.commit()
    except:
        pass


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

    @staticmethod
    def show_help():
        print('send - отправка сообщения\n'
              'list - список подключенных пользователей\n'
              'contacts - список контактов\n'
              'add_contact\n'
              'del_contact\n'
              'exit - выход\n'
              'help - вывод подсказки')

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
                msg = get_message(sock)
                if ACTION in msg and msg[ACTION] == 'message' and SENDER in msg and MESSAGE in msg \
                   and msg[DESTINATION] == name:
                    LOG.debug(f'Got message from {msg[SENDER]}')
                    print(f'\nПолучено сообщение от пользователя {msg[SENDER]}:\n{msg[MESSAGE]}')
                # если пришел код 445 - пользователь-получатель не существует
                elif RESPONSE in msg:
                    if msg[RESPONSE] == '445':
                        LOG.info('Server has responded with status 445 - Destination user does not exist')
                        print('Ошибка: Получатель не найден')
                # вывод списка пользователей
                elif USER_LIST in msg:
                    print(f'Список пользователей: {msg[USER_LIST]}')
                # вывод списка контактов
                elif CONTACT_LIST in msg:
                    print(f'Список контактов: {msg[CONTACT_LIST]}')
                else:
                    LOG.warning(f'Got incorrect message')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError):
                LOG.critical(f'Соединение разорвано')
                break

    @log
    def create_msg_presence(self, account_name='guest'):
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
        contact_name = input('Введите имя контакта')
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
        contact_name = input('Введите имя контакта')
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
    def create_message(self, sock, account_name='guest'):
        """
        Возвращает сформированное сообщение или завершает процесс
        :param sock:
        :param account_name:
        :return msg:
        """
        dst_name = input('Кому:\n>>')
        msg_body = input('Введите текст сообщения или ] для закрытия программы:\n>> ')
        if msg_body == ']':
            sock.close()
            LOG.info(f'{account_name} завершил программу')
            sys.exit(0)
        else:
            msg = {
                ACTION: 'message',
                TIME: time(),
                ACCOUNT_NAME: account_name,
                MESSAGE: msg_body,
                DESTINATION: dst_name
            }
            return msg

    @log
    def check_response(self, response):
        """
        Проверяет ответ на приветственное сообщение.
        Возвращает True в случае успешного подключения и False при ошибке
        :param response:
        """
        if RESPONSE in response:
            if response[RESPONSE] == '200':
                LOG.info('Server has responded with status 200 - OK')
                print('Server has responded with status 200 - OK')
                return True
            elif response[RESPONSE] == '444':
                LOG.info('Server has responded with status 444 - Login is incorrect')
                print('Логин занят, попробуйте другой')
                return False
            # elif response[RESPONSE] == '445':
            #     LOG.info('Server has responded with status 445 - Destination user does not exist')
            #     print('Отправитель не найден')
            #     return False
            else:
                LOG.critical('Server has responded with error 400 - Bad Request')
                print('Server has responded with error 400 - Bad Request')
                return False
        raise ValueError

    @log
    def console_interact(self, sock, name):
        """
        Запрашивает и обрабатывает команды пользователя.
        :param sock:
        :param name:
        """
        while True:
            sleep(0.5)
            choice = input(f'Пользователь <<{name}>>\nВведите команду или help для помощи:\n>>')

            # вывод подсказки
            if choice == 'help':
                self.show_help()

            # отправка сообщения
            elif choice == 'send':
                try:
                    send_message(sock, self.create_message(sock, name))
                except:
                    print(f'Соединение с сервером было разорвано')
                    LOG.critical(f'Соединение с сервером было разорвано')
                    sys.exit(1)

            # вывод списка пользователей
            elif choice == 'list':
                try:
                    send_message(sock, self.create_msg_list(name))
                except:
                    print(f'Соединение с сервером было разорвано')
                    LOG.critical(f'Соединение с сервером было разорвано')
                    sys.exit(1)

            # вывод списка пользователей
            elif choice == 'add_contact':
                try:
                    send_message(sock, self.create_msg_add_contact(name))
                except:
                    print(f'Соединение с сервером было разорвано')
                    LOG.critical(f'Соединение с сервером было разорвано')
                    sys.exit(1)

            # вывод списка пользователей
            elif choice == 'del_contact':
                try:
                    send_message(sock, self.create_msg_del_contact(name))
                except:
                    print(f'Соединение с сервером было разорвано')
                    LOG.critical(f'Соединение с сервером было разорвано')
                    sys.exit(1)

            # вывод списка контактов
            elif choice == 'contacts':
                try:
                    send_message(sock, self.create_msg_get_contacts(name))
                except:
                    print(f'Соединение с сервером было разорвано')
                    LOG.critical(f'Соединение с сервером было разорвано')
                    sys.exit(1)

            # выход
            elif choice == 'exit':
                send_message(sock, self.create_msg_exit(name))
                sleep(1)
                break
            else:
                print('Команда не распознана\n')
                self.show_help()


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
        parser.add_argument('-n', '--name')
        namespace = parser.parse_args(sys.argv[1:])
        server_name = namespace.addr
        server_port = namespace.port
        client_name = namespace.name

        if not 1023 < server_port < 65536:
            LOG.warning(f'Не удалось подключиться к порту {server_port}')
            print(f'Указан неверный порт, используется порт по умолчанию: {DEFAULT_PORT}')
            server_port = DEFAULT_PORT

        return server_name, server_port, client_name

    def launch(self):
        server_name, server_port, client_name = self.parse_arguments()
        LOG.info(f'Подключение к {server_name}:{server_port}')

        if not client_name:
            client_name = input('Введите Ваше имя:')

        try:
            # client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect((server_name, server_port))
            LOG.info(f'Connect to {server_name}:{server_port}')
            send_message(self.client_socket, self.create_msg_presence(client_name))
            resp = get_message(self.client_socket)
            if not self.check_response(resp):
                sleep(1)
                sys.exit(1)

            LOG.info(f'Got message from server with response {resp}')
        except ConnectionRefusedError:
            print('Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение')
            sys.exit(1)
        else:

            receiver = Thread(target=self.print_message, args=(self.client_socket, client_name))
            receiver.daemon = True
            receiver.start()

            sender = Thread(target=self.console_interact, args=(self.client_socket, client_name))
            sender.daemon = True
            sender.start()

            while True:
                sleep(1)
                if receiver.is_alive() and sender.is_alive():
                    continue
                break


def main():
    c = Client()
    c.launch()


if __name__ == '__main__':
    main()
