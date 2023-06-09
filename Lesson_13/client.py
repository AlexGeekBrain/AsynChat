# -*- coding: utf-8 -*-
import logging
import logs.config_client_log
import argparse
import sys

from PyQt5.QtWidgets import QApplication

from common.variables import *
from common.errors import ServerError
from common.decos import log

from client.database import ClientDatabase
from client.transport import ClientConnection
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog


logger = logging.getLogger('client')


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.addr
    port = namespace.port
    client_name = namespace.name

    if not 1023 < port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {port}. Допустимы адреса с 1024 до 65535')
        exit(1)

    return addr, port, client_name


if __name__ == '__main__':
    addr, port, client_name = arg_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()

        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {addr} , порт: {port}, имя пользователя: {client_name}')

    db = ClientDatabase(client_name)

    try:
        connect = ClientConnection(port, addr, db, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    connect.setDaemon(True)
    connect.start()

    main_window = ClientMainWindow(db, connect)
    main_window.make_connection(connect)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    connect.transport_shutdown()
    connect.join()
