from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import json
import sys
import time
import argparse

import logging
import log.client_log_config

from utils import *
from decorators import Log
from metaclasses import ClientVerifier
from constants import (ACTION, ACCOUNT_NAME, ERROR, IP_ADDRESS,
    MESSAGE, MESSAGE_TEXT, PORT, PRESENCE, RESPONSE, TIME, USER, 
    RECIPIENT, SENDER, EXIT)


logger = logging.getLogger('client')


class ClientSend(Thread, metaclass=ClientVerifier):

    def __init__(self, sock, account_name):
        self.sock = sock
        self.account_name = account_name
        super().__init__()

    def create_message(self):
        send = input('Кому отправить: ')
        text = input('Сообщение: ')
        message = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            RECIPIENT: send,
            TIME: time.time(),
            MESSAGE_TEXT: text
        }
        logger.debug(f"Создано {message}-сообщение для пользователя '{self.account_name}'")
        return message
    
    def create_exit(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name,
        }
    
    def run(self):
        print('Для отправки сообщений введите: "send"\nДля выхода: "exit"\n')
        while True:
            mode = input('Введите команду: ')
            if mode == 'send':
                send_message(self.sock, self.create_message())
            elif mode == 'exit':
                send_message(self.sock, self.create_exit())
                self.sock.close()
                logger.info('Соединение завершено пользователем.')
                print('Всего доброго!\n')
                time.sleep(0.8)
                break
            else:
                print('Введите корректную команду: "send" или "exit"')
    
    
class ClientRead(Thread, metaclass=ClientVerifier):
    def __init__(self, sock, recipient):
        self.sock = sock
        self.recipient = recipient
        super().__init__()


    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if (ACTION in message and message[ACTION] == MESSAGE
                        and RECIPIENT in message and message[RECIPIENT] == self.recipient):
                    print(f"\nПолучено сообщение от пользователя '{message[SENDER]}': '{message[MESSAGE_TEXT]}'.")
                    logger.info(f"Получено сообщение от пользователя '{message[SENDER]}': '{message[MESSAGE_TEXT]}'.")
                else:
                    logger.error(f"Получено некорректное сообщение: '{message}'.")
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f"Соединение с сервером разорвано.")
                break


def create_presence(account_name='NoName'):
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f"Создано {PRESENCE}-сообщение для пользователя '{account_name}'")
    return message


@Log()
def parse_server_response(message):
    logger.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    return ValueError


@Log()
def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('address', default=IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.address
    port = namespace.port
    user = namespace.name

    if port < 1024 or port > 65535:
        logger.error(f"Выбран неверный порт {port}, необходим диапазон: 1024 - 65535.")
        sys.exit(1)

    if user is None:
        user = input('Введите свое имя: ')

    return addr, port, user



def main():
    
    addr, port, user = parse_cli_args()
    print(f"Приложение клиента '{user}'.\n")

    logger.info(f'Запуск клиента с параметрами: '
                f'адрес сервера: {addr}, порт сервера: {port}, имя клиента: {user}.')

    try:
        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((addr, port))
        send_message(connection, create_presence(user))
        answer = parse_server_response(get_message(connection))
        logger.info(f"Принят ответ сервера: '{answer}'.")
        print(f'Установлено соединение с сервером, ответ сервера: {answer}.')
    except (ValueError, json.JSONDecodeError):
        logger.error('Некорректное сообщение от сервера.')
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(f"Подключение к серверу '{addr}:{port}' не установлено.")
        sys.exit(1)
        
    else:
        monitor_read = ClientRead(connection, user)
        monitor_read.daemon = True
        monitor_read.start()

        monitor_send = ClientSend(connection, user)
        monitor_send.daemon = True
        monitor_send.start()

        while True:
            time.sleep(1)
            if monitor_send.is_alive() and monitor_read.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
