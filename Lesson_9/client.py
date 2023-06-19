from socket import *
from threading import Thread
import json
import sys
import time
import argparse

import logging
import log.client_log_config

from utils import *
from decorators import Log
from constants import (ACTION, ACCOUNT_NAME, ERROR, IP_ADDRESS,
    MESSAGE, MESSAGE_TEXT, PORT, PRESENCE, RESPONSE, TIME, USER, 
    RECIPIENT, SENDER, EXIT)


logger = logging.getLogger('client')


@Log()
def process_message(sock, recipient):
    while True:
        try:
            message = get_message(sock)
            if (ACTION in message and message[ACTION] == MESSAGE
                    and RECIPIENT in message and message[RECIPIENT] == recipient):
                print(f"\nПолучено сообщение от пользователя '{message[SENDER]}': '{message[MESSAGE_TEXT]}'.")
                logger.info(f"Получено сообщение от пользователя '{message[SENDER]}': '{message[MESSAGE_TEXT]}'.")
            else:
                logger.error(f"Получено некорректное сообщение: '{message}'.")
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            logger.critical(f"Соединение с сервером разорвано.")
            break


@Log()
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
def create_message(account_name='NoName'):
    send = input('Кому отправить: ')
    text = input('Сообщение: ')
    message = {
        ACTION: MESSAGE,
        SENDER: account_name,
        RECIPIENT: send,
        TIME: time.time(),
        MESSAGE_TEXT: text
    }
    logger.debug(f"Создано {MESSAGE}-сообщение для пользователя '{account_name}'")
    return message


@Log()
def create_exit(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
    }


@Log()
def parse_server_response(message):
    logger.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: OK'
        return f'400: {message[ERROR]}'
    return ValueError


@Log()
def commands(sock, sender):
    print('Для отправки сообщений введите: "send"\nДля выхода: "exit"\n')
    while True:
        mode = input('Введите команду: ')
        if mode == 'send':

            send_message(sock, create_message(sender))
        elif mode == 'exit':
            send_message(sock, create_exit(sender))
            sock.close()
            logger.info('Соединение завершено пользователем.')
            print('Всего доброго!\n')
            time.sleep(0.8)
            break
        else:
            print('Введите корректную команду: "send" или "exit"')


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
        logger.error(f"Выбран неверный порт {port}, требуется из диапазона: 1024 - 65535.")
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
        monitor = Thread(target=process_message, args=(connection, user))
        monitor.daemon = True
        monitor.start()

        thread_icl = Thread(target=commands, args=(connection, user))
        thread_icl.daemon = True
        thread_icl.start()

        while True:
            time.sleep(11)
            if thread_icl.is_alive() and monitor.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
