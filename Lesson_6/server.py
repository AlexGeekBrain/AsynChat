from socket import *

import json
import sys
import time

import logging
import log.server_log_config

import inspect


logger = logging.getLogger('server')


def log(func):
     def wrapper(*args, **kwargs):
          logger.info(f'Вызов функции {func.__name__} с агрументами {args, kwargs}')
          logger.info(f'Функция {func.__name__} вызвана из функции {inspect.stack()[1][3]}')
          return func(*args, **kwargs)
     return wrapper


@log
def get_response(json_data):
    response = 200
    alert = 'OK'

    logger.debug(f'Разбор сообщений от клиента: {json_data}')
    if 'action' not in json_data or 'time' not in json_data:
        response = 400
        alert = 'Неправильный запрос'
    elif 'user' not in json_data:
        response = 404
        alert = 'Пользователь не обнаружен'
    response = {
        'response': response,
        'time': time.time(),
        'alert': alert
    }
    return response
    

def main():  
    if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
    else:
            port = 7777 
    if port < 1024 or port > 65535:
        logger.critical('Диапазон портов должен быть от 1024 до 65535')
        sys.exit(1)

    if '-a' in sys.argv:
        addr = sys.argv[sys.argv.index('-a') + 1]
    else:
        addr = ''

    logger.info(f'Сервер запущен на порту: {port}')

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((addr, port))
    s.listen(5)

    while True:
        client, addr = s.accept()
        data = client.recv(1024)
        json_data = json.loads(data.decode('utf-8'))
        print(json_data)
        response = get_response(json_data)
        client.send(json.dumps(response).encode('utf-8'))
        client.close()


if __name__ == '__main__':
    main()
