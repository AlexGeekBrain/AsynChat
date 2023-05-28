import sys
import socket
import select
import logging
import argparse
import log.server_log_config

from utils import *
from decorators import Log
from descriptors import Port
from metaclasses import ServerVerifier
from constants import (ACTION, ACCOUNT_NAME, ERROR, MAX_CONNECTIONS,
                       PORT, PRESENCE, RESPONSE, TIME, USER, MESSAGE, 
                       RECIPIENT, SENDER, MESSAGE_TEXT, EXIT)


logger = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_addr, listen_port):
        self.addr = listen_addr
        self.port = listen_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.messages = []
        self.names = {}

    def listen(self):
        logger.info(f'Запуск сервера по адресу: {self.addr}, порт: {self.port}.')
        self.socket.bind((self.addr, self.port))
        self.socket.settimeout(0.4)
        self.socket.listen(MAX_CONNECTIONS)

    def run(self):
        self.listen()

        while True:
            try:
                client, client_address = self.socket.accept()
            except OSError:
                pass  
            else:
                print(f'Установлено соединение с клиентом: {client_address}')
                logger.info(f'Установлено соединение с клиентом: {client_address}')
                self.clients.append(client)
            finally:
                read_list = []
                write_list = []
                error_list = []
                try:
                    read_list, write_list, error_list = select.select(self.clients, self.clients, [], 1)
                except OSError:
                    pass

                if read_list:
                    for client in read_list:
                        try:
                            self.client_message(get_message(client), client)
                        except OSError:
                            logger.info(f"Клиент '{client.getpeername()}' отключился.")
                            print(f"Клиент '{client.getpeername()}' отключился.")
                            self.clients.remove(client)

                for msg in self.messages:
                    try:
                        self.process_message(msg, write_list)
                    except OSError:
                        logger.info(f"Связь с клиентом '{msg[RECIPIENT]}' потеряна.")
                        print(f"Связь с клиентом '{msg[RECIPIENT]}' потеряна.")
                        self.clients.remove(self.names[msg[RECIPIENT]])
                        del self.names[msg[RECIPIENT]]
                self.messages.clear()


    def client_message(self, message, client):
        if (ACTION in message and message[ACTION] == PRESENCE
                and TIME in message and USER in message):
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, {RESPONSE: 200})
            else:
                response = {RESPONSE: 400}
                response[ERROR] = 'Пользователь уже существует.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif (ACTION in message and message[ACTION] == MESSAGE and RECIPIENT in message
            and TIME in message and SENDER in message and MESSAGE_TEXT in message):
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            print(f'Клиент отключился.')
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            send_message(client, {RESPONSE: 400})
            return
    


    def process_message(self, message, sockets):
        if message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] in sockets:
            send_message(self.names[message[RECIPIENT]], message)
            logger.info(f'Пользователю {message[RECIPIENT]} отправлено сообщение от пользователя {message[SENDER]}.')
        elif message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] not in sockets:
            raise ConnectionError
        else:
            print(f'Пользователь {message[RECIPIENT]} не найден, отправка сообщения невозможна.')


@Log()
def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='', nargs='?')
    parser.add_argument('-p', default=PORT, type=int, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_addr = namespace.a
    listen_port = namespace.p

    return listen_addr, listen_port


def main():
    print('Сервер запущен, ожидание клиентов....')
    logger.debug('Запуск сервера')
    addr, port = parse_cli_args()
    server = Server(addr, port)
    server.run()
    

if __name__ == '__main__':
    main()
