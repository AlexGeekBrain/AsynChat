from socket import *

import sys
import inspect
import select
import logging
import log.server_log_config

from utils import *
from decorators import Log
from constants import (ACTION, ACCOUNT_NAME, ERROR, MAX_CONNECTIONS,
                       PORT, PRESENCE, RESPONSE, TIME, USER)


logger = logging.getLogger('server')


@Log()
def parse_client_response(message):
    logger.debug(f'Разбор сообщения от клиента: {message}')
    if (ACTION in message and TIME in message and USER in message
            and message[USER][ACCOUNT_NAME] == 'User'):
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
        }


@Log()
def read_requests(read_clients, all_clients):
    responses = {}

    for client in read_clients:
        try:
            message_from_client = get_message(client)
            print(f'Получено сообщение: {message_from_client}')
            logger.debug(f'Получено сообщение: {message_from_client}')
            responses[client] = message_from_client
        except:
            print(f'Клиент {client.getpeername()} отключился.')
            logger.info(f'Клиент {client.getpeername()} отключился.')
            all_clients.remove(client)
    return responses


@Log()
def write_responses(requests, write_clients, all_clients):

    for client in write_clients:
        if client in requests:
            try:
                response = parse_client_response(requests[client])
                logger.info(f'Создан ответ клиенту: {response}')
                send_message(client, response)
            except:
                print(f'Клиент {client.getpeername()} отключился.')
                logger.info(f'Клиент {client.getpeername()} отключился.')
                client.close()
                all_clients.remove(client)


def main():

    try:
        if '-a' in sys.argv:
            idx = sys.argv.index('-a')
            listening_address = sys.argv[idx + 1]
        else:
            listening_address = ''
    except IndexError:
        logger.critical('После параметра "-a" не указан ip-адрес.')
        sys.exit(1)

    try:
        if '-p' in sys.argv:
            idx = sys.argv.index('-p')
            listening_port = int(sys.argv[idx + 1])
        else:
            listening_port = PORT
        if listening_port < 1024 or listening_port > 65535:
            raise ValueError
    except IndexError:
        logger.critical('После параметра "-p" не указан номер порта.')
        sys.exit(1)
    except ValueError:
        logger.error(f'Выбран неверный порт {listening_port}, требуется из диапазона: 1024 - 65535.')
        sys.exit(1)

    print('Сервер запущен, ожидание клиентов....')
    logger.info(f'Запуск сервера по адресу: {listening_address}, порт: {listening_port}.')

    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((listening_address, listening_port))
    connection.listen(MAX_CONNECTIONS)
    connection.settimeout(0.4)

    clients = []

    while True:
        try:
            client, client_address = connection.accept()
        except OSError:
            pass  
        else:
            print(f'Установлено соединение с клиентом: {client_address}')
            logger.info(f'Установлено соединение с клиентом: {client_address}')
            clients.append(client)
        finally:
            read_list = []
            write_list = []
            error_list = []
            try:
                read_list, write_list, error_list = select.select(clients, clients, [], 1)
            except:
                pass

            requests = read_requests(read_list, clients)
            if requests:
                write_responses(requests, write_list, clients)


if __name__ == '__main__':
    main()
