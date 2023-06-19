from socket import *

import sys
import inspect
import select
import logging
import log.server_log_config

from utils import *
from decorators import Log
from constants import (ACTION, ACCOUNT_NAME, ERROR, MAX_CONNECTIONS,
                       PORT, PRESENCE, RESPONSE, TIME, USER, MESSAGE, 
                       RECIPIENT, SENDER, MESSAGE_TEXT, EXIT)


logger = logging.getLogger('server')


@Log()
def client_message(message, messages, client, clients, names):
    if (ACTION in message and message[ACTION] == PRESENCE
            and TIME in message and USER in message):
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        else:
            response = {RESPONSE: 400}
            response[ERROR] = 'Пользователь уже существует.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif (ACTION in message and message[ACTION] == MESSAGE and RECIPIENT in message
          and TIME in message and SENDER in message and MESSAGE_TEXT in message):
        messages.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        print(f'Клиент отключился.')
        del names[message[ACCOUNT_NAME]]
        return
    else:
        send_message(client, {RESPONSE: 400})
        return
    

@Log()
def process_message(message, names, sockets):
    if message[RECIPIENT] in names and names[message[RECIPIENT]] in sockets:
        send_message(names[message[RECIPIENT]], message)
        logger.info(f'Пользователю {message[RECIPIENT]} отправлено сообщение от пользователя {message[SENDER]}.')
    elif message[RECIPIENT] in names and names[message[RECIPIENT]] not in sockets:
        raise ConnectionError
    else:
        print(f'Пользователь {message[RECIPIENT]} не найден, отправка сообщения невозможна.')



def main():

    try:
        if '-a' in sys.argv:
            idx = sys.argv.index('-a')
            addr = sys.argv[idx + 1]
        else:
            addr = ''
    except IndexError:
        logger.critical('После параметра "-a" не указан ip-адрес.')
        sys.exit(1)

    try:
        if '-p' in sys.argv:
            idx = sys.argv.index('-p')
            port = int(sys.argv[idx + 1])
        else:
            port = PORT
        if port < 1024 or port > 65535:
            raise ValueError
    except IndexError:
        logger.critical('После параметра "-p" не указан номер порта.')
        sys.exit(1)
    except ValueError:
        logger.error(f'Выбран неверный порт {port}, требуется из диапазона: 1024 - 65535.')
        sys.exit(1)

    print('Сервер запущен, ожидание клиентов....')

    logger.info(f'Запуск сервера по адресу: {addr}, порт: {port}.')

    connection = socket(AF_INET, SOCK_STREAM)
    connection.bind((addr, port))
    connection.listen(MAX_CONNECTIONS)
    connection.settimeout(0.4)

    clients = []
    messages = []
    names = {}

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
            except OSError:
                pass

            if read_list:
                for client in read_list:
                    try:
                        client_message(get_message(client), messages, client, clients, names)
                    except:
                        logger.info(f"Клиент '{client.getpeername()}' отключился.")
                        print(f"Клиент '{client.getpeername()}' отключился.")
                        clients.remove(client)

            for msg in messages:
                try:
                    process_message(msg, names, write_list)
                except:
                    logger.info(f"Связь с клиентом '{msg[RECIPIENT]}' потеряна.")
                    print(f"Связь с клиентом '{msg[RECIPIENT]}' потеряна.")
                    clients.remove(names[msg[RECIPIENT]])
                    del names[msg[RECIPIENT]]
            messages.clear()


if __name__ == '__main__':
    main()
