from socket import *

import json
import sys
import time
import argparse

import logging
import log.client_log_config

import inspect


logger = logging.getLogger('client')


def log(func):
     def wrapper(*args, **kwargs):
          logger.info(f'Вызов функции {func.__name__} с агрументами {args, kwargs}')
          logger.info(f'Функция {func.__name__} вызвана из функции {inspect.stack()[1][3]}')
          return func(*args, **kwargs)
     return wrapper


@log
def create_presence(account_name='Alex'):
    data = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': account_name,
            'status': 'Hi!'
        }
    }
    logger.debug(f'Сформировано сообщение для пользователя {account_name}')
    return data


@log
def get_status(msg):
    logger.debug(f'Разбор сообщений от сервера {msg}')
    if 'response' in msg:
        if msg['response'] == 200:
            return '200: OK'
        return '400: ERROR'
    raise ValueError


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='127.0.0.1', nargs='?')
    parser.add_argument('port', default=7777, type=int, nargs='?')
    return parser


def main():
    
    parser = arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.addr
    port = namespace.port

    if port < 1024 or port > 65535:
        logger.critical('Диапазон портов должен быть от 1024 до 65535')    
        sys.exit(1)

    logger.info(f'Запущен клиент с параметрами: '
                f'Адрес сервера: {addr}, порт: {port}')

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((addr, port))
    data = create_presence()
    s.send(json.dumps(data).encode('utf-8'))
    msg = s.recv(1024)
    json_data = json.loads(msg.decode('utf-8'))
    status_code = get_status(json_data)
    print(status_code)


if __name__ == '__main__':
    main()