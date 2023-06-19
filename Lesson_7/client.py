from socket import *

import json
import sys
import time

import logging
import log.client_log_config

from utils import *
from decorators import Log
from constants import ACTION, ACCOUNT_NAME, ERROR, IP_ADDRESS,\
    MESSAGE, MESSAGE_TEXT, PORT, PRESENCE, RESPONSE, TIME, USER


logger = logging.getLogger('client')


@Log()
def create_presence(account_name='User'):
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
def create_message(msg, account_name='User'):
    message = {
        ACTION: MESSAGE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        },
        MESSAGE_TEXT: msg
    }
    logger.debug(f"Создано {MESSAGE}-сообщение для пользователя '{account_name}'")
    return message


@Log()
def parse_server_response(message):
    logger.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    return ValueError


def main():
    
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = IP_ADDRESS
        server_port = PORT
        logger.info('Установлены параметры по умолчанию: '
                    f'адрес сервера: {server_address}, порт: {server_port}.')
    except ValueError:
        logger.error(f'Выбран неверный порт {server_port}, требуется из диапазона: 1024 - 65535.')
        sys.exit(1)

    logger.info(f'Запуск клиента с параметрами: '
                f'адрес сервера: {server_address}, порт: {server_port}.')

    try:
        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(connection, message_to_server)
        answer = parse_server_response(get_message(connection))
        logger.info(f"Принят ответ сервера: '{answer}'")
        print(f'Установлено соединение с сервером, ответ сервера: {answer}.')
    except (ValueError, json.JSONDecodeError):
        logger.error('Некорректное сообщение от сервера.')
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(f"Подключение к серверу '{server_address}:{server_port}' не установлено.")
        sys.exit(1)

    mode = input('Команды:\n"msg" - для отправки сообщений\n"exit" - для выхода\n')
    if mode == 'msg':
        print('Отправка сообщений')
    if mode == 'exit':
            connection.close()
            logger.info('Соединение завершено пользователем.')
            print('Всего доброго!')
            sys.exit(0)
    while True:
        msg = input('Введите сообщение: ')
        send_message(connection, create_message(msg))
        if msg == 'exit':
            connection.close()
            logger.info('Соединение завершено пользователем.')
            print('Всего доброго!')
            sys.exit(0)
        

if __name__ == '__main__':
    main()
