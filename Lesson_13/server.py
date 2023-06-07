import os
import socket
import sys
import argparse
import logging
import select
import configparser

from threading import Lock, Thread

import logs.config_server_log

from common.variables import *
from common.utils import *
from common.decos import log

from descryptors import Port
from metaclasses import ServerMaker
from server_database import ServerStorage
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer


logger = logging.getLogger('server')

new_connection = False
conflag_lock = Lock()

@log
def arg_parser(default_port, default_addr):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', default=default_addr, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.a
    port = namespace.p
    return addr, port


class Server(Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, addr, port, db):
        self.addr = addr
        self.port = port
        self.db = db

        self.clients = []
        self.messages = []
        self.names = dict()
        super().__init__()

    def init_socket(self):
        logger.info(f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются подключения: {self.addr}.')
        
        connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect.bind((self.addr, self.port))
        connect.settimeout(0.5)

        self.sock = connect
        self.sock.listen()

    def run(self):
        global new_connection
        self.init_socket()

        while True:
            try:
                client, client_addr = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_addr}')
                self.clients.append(client)

            read_list = []
            write_list = []
            error_list = []
            
            try:
                if self.clients:
                    read_list, write_list, error_list = select.select(self.clients, self.clients, [], 1)
            except OSError as err:
                logger.error(f'Ошибка работы с сокетами: {err}')

            if read_list:
                for client in read_list:
                    try:
                        self.process_client_message(get_message(client), client)
                    except (OSError):
                        logger.info(f'Клиент {client.getpeername()} отключился от сервера.')
                        for name in self.names:
                            if self.names[name] == client:
                                self.db.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client)
                        with conflag_lock:
                            new_connection = True

            for message in self.messages:
                try:
                    self.process_message(message, write_list)
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    logger.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    self.db.user_logout(message[DESTINATION])
                    del self.names[message[DESTINATION]]
                    with conflag_lock:
                        new_connection = True
            self.messages.clear()


    def process_message(self, message, socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in socks:
            send_message(self.names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')


    def process_client_message(self, message, client):
        global new_connection
        logger.debug(f'Разбор сообщения от клиента : {message}')

        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.db.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return

        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message and self.names[message[SENDER]] == client:
            if message[DESTINATION] in self.names:
                self.messages.append(message)
                self.db.process_message(message[SENDER], message[DESTINATION])
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                send_message(client, response)
            return

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.db.user_logout(message[ACCOUNT_NAME])
            logger.info(f'Клиент {message[ACCOUNT_NAME]} корректно отключился от сервера.')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.db.get_contacts(message[USER])
            send_message(client, response)

        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.db.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.db.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.db.users_list()]
            send_message(client, response)
            
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def config_load():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


def main():
    config = config_load()
    addr, port = arg_parser(config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])
    db = ServerStorage(os.path.join(config['SETTINGS']['Database_path'], config['SETTINGS']['Database_file']))

    server = Server(addr, port, db)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage('Сервер работает')
    main_window.active_clients_table.setModel(gui_create_model(db))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()


    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(gui_create_model(db))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False


    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(db))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()


    def server_config():
        global config_window
        
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    
    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                with open(f"{dir_path}/{'server.ini'}", 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

   
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()


if __name__ == '__main__':
    main()
