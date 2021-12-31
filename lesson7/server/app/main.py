import os
import threading

from db_handlers import create_user, add_history, get_obj_by_login, add_contact, delete_contact, get_contacts

import argparse
from socket import socket, AF_INET, SOCK_STREAM
import sys
from time import time

from PyQt5.QtWidgets import QApplication
import select

from server.common.utils import send_encrypted_message, get_encrypted_message
from server.common.constants import DEFAULT_PORT, TIME, ACTION, RESPONSE, MAX_CONNECTIONS, USER_LIST, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, CONTACT_NAME, CONTACT_LIST, PASSWD, ENCODING, CONTACT
import logging

from server.app.decorators import log


import dis
import hmac
import hashlib
import binascii
from metaclasses import ServerSocket, ServerVerifier
from server_gui import ServerGUI

from Crypto.PublicKey import RSA


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
        self.secret_keys = {}
        keys = RSA.generate(2048, os.urandom)
        self.public_key = keys.public_key().export_key()

    @log
    def process_client_message(self, sock, msg, msg_list):
        """
        Метод проверяет тип входящего сообщения, проверяет корректность сообщения
        и отправляет соответствующий ответ клиенту
        """
        resp = {RESPONSE: ''}
        # Обработка приветственного сообщения
        if ACTION in msg and msg[ACTION] == 'presence' and TIME in msg:
            self.generate_secret_key(sock)
            send_encrypted_message(sock, {RESPONSE: '200'})
            self.client_sockets[sock.getpeername()[0]+str(sock.getpeername()[1])] = sock
            return
        # Обработка авторизации
        if ACTION in msg and msg[ACTION] == 'login' and TIME in msg and ACCOUNT_NAME in msg:
            LOG.debug(f'{msg[ACCOUNT_NAME]}\'s message is correct')
            if msg[ACCOUNT_NAME] in self.active_clients.values():  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                resp = {RESPONSE: '444'}
            else:
                # проверка существования пользователя
                if self.server_authenticate(sock):
                    user = get_obj_by_login(msg[ACCOUNT_NAME])
                    if user:
                        if self.check_credentials(user, self.check_password(user)):
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
        # Обработка сообщения о регистрации
        elif ACTION in msg and msg[ACTION] == 'register' and TIME in msg and ACCOUNT_NAME in msg and PASSWD in msg:
            user = get_obj_by_login(msg[ACCOUNT_NAME])
            if not user:
                passwd = self.check_password(msg[PASSWD])
                create_user(msg[ACCOUNT_NAME], passwd, '')
                send_encrypted_message(sock, {RESPONSE: '211'})
            else:
                LOG.critical(f'{msg[ACCOUNT_NAME]} name is busy')
                send_encrypted_message(sock, {RESPONSE: '444'})
            return
        # Обработка запроса списка пользователей онлайн
        elif ACTION in msg and msg[ACTION] == 'list' and TIME in msg and ACCOUNT_NAME in msg:
            print(f'msg22 - {msg}')
            send_encrypted_message(sock, {RESPONSE: "202", USER_LIST: self.online_users})
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
        # elif ACTION in msg and msg[ACTION] == 'exit' and TIME in msg and ACCOUNT_NAME in msg:
        #     if msg[ACCOUNT_NAME] in self.clients.keys():
        #         del self.clients[msg[ACCOUNT_NAME]]
        #         LOG.info(f'{msg[ACCOUNT_NAME]} has disconnected')
        #     return
        else:
            LOG.critical(f'{msg[ACCOUNT_NAME]}\'s message is incorrect')
            LOG.debug(f'{msg}')
            send_encrypted_message(sock, {RESPONSE: '400'})
            return

    def generate_secret_key(self, sock):
        r = os.urandom(32)

        print(sock.getpeername()[0]+str(sock.getpeername()[1]))

    def check_password(self, sock, user):
        """
        Проверка пароля пользователя. Отправляет случайную строку клиенту,
        получает ответ, сравнивает хеши
        """
        random_string = os.urandom(32)
        passwd = hashlib.pbkdf2_hmac('sha256', user.passwd_hash.encode(ENCODING), random_string, 100000)
        reg_msg = {RESPONSE: '212', 'salt': random_string}
        send_encrypted_message(sock, reg_msg)
        ans = get_encrypted_message(sock)
        if ans[PASSWD] == passwd:
            print('OK')
        else:
            print('Not OK')

    @log
    def parse_arguments(self):
        """
        Метод парсит аргументы запуска сервера и проверяет их корректность.
        Обновляет свойства адрес и порт.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--addr', default=self.addr)
        parser.add_argument('-p', '--port', type=int, default=self.port)
        namespace = parser.parse_args(sys.argv[1:])
        self.addr = namespace.addr
        self.port = namespace.port
    #
    # def check_credentials(self, user, passwd):
    #     print(user.password_hash, passwd)
    #     if user.password_hash == passwd:
    #         return True
    #     return False

    @property
    def online_users(self):
        """
        Возврашает словарь с пользователями онлайн
        """
        online_dict = {}
        for key, value in self.active_clients.items():
            online_dict[value[0]] = key
        return online_dict

    # def server_authenticate(self, sock):
    #     message = os.urandom(32)
    #     sock.send(message)
    #
    #     hash = hmac.new(SECRET_KEY, message, 'sha256')
    #     digest = hash.digest()
    #
    #     response = sock.recv(len(digest))
    #     return hmac.compare_digest(digest, response)

    def run(self):
        """Метод запуска сервера"""
        messages = []
        self.parse_arguments()

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
                    print(f'hosts_who_send: {hosts_who_send}')
                    print(f'hosts_who_listen: {hosts_who_listen}')
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
                            # del self.active_clients[key_host]

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
