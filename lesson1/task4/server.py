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

LOG = logging.getLogger('app.server')


@log
def process_client_message(sock, msg, msg_list, client_list):
    """
    Функция проверяет тип и корректность запроса.
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
def parse_arguments():
    """
    Функция парсит аргументы запуска сервера и проверяет их корректность.
    Возвращает прослушиваемый адрес и порт.
    Если аргументы не заданы, возвращает значения по умолчанию.
    :return listen_name, listen_port:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default='')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT)
    namespace = parser.parse_args(sys.argv[1:])
    listen_name = namespace.addr
    listen_port = namespace.port

    if not 1023 < listen_port < 65536:
        LOG.warning(f'Не удалось подключиться к порту {listen_port}')
        print(f'Указан неверный порт, используется порт по умолчанию: {DEFAULT_PORT}')
        listen_port = DEFAULT_PORT

    return listen_name, listen_port


def main():
    listen_name, listen_port = parse_arguments()
    server_socket = socket(AF_INET, SOCK_STREAM)

    clients = {}  # словарь {логин: сокет, }
    messages = []  # список кортежей [(отправитель, сообщение, получатель), ]

    try:
        server_socket.bind((listen_name, listen_port))
    except OSError:
        print(f'Cannot bind to {listen_name}:{listen_port}. Switching to default params')
        LOG.critical(f'Cannot bind to {listen_name}:{listen_port}')
        server_socket.bind(('', listen_port))
    finally:
        server_socket.settimeout(0.5)

    server_socket.listen(MAX_CONNECTIONS)
    LOG.info(f'Listen {listen_name}:{listen_port}')
    print(f'Server has started.\nListen {listen_name}:{listen_port}')

    while True:
        try:
            client_socket, addr = server_socket.accept()
        except OSError:
            pass
        else:
            print(f'Host {addr} has connected')
            LOG.info(f'Host {addr} has connected')

            # Получение приветственного сообщения
            process_client_message(client_socket, get_message(client_socket), [], clients)

        hosts_who_send, hosts_who_listen = [], []

        try:
            if clients:
                hosts_who_send, hosts_who_listen, _ = select.select(clients.values(), clients.values(), [], 0)
        except OSError:
            pass

        if hosts_who_send:
            for host in hosts_who_send:
                try:
                    process_client_message(host, get_message(host), messages, clients)
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


if __name__ == '__main__':
    main()
