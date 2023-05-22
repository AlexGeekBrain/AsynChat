from socket import *
import json
import sys
import time


def create_presence():
    data = {
        'action': 'presence',
        'time': time.time(),
        'user': {
            'account_name': 'Alex',
            'status': 'Hi!'
        }
    }
    return data


def get_status(msg):
    if 'response' in msg:
        if msg['response'] == 200:
            return '200: OK'
        return '400: ERROR'
    raise ValueError


def main():
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
        if port < 1024 or port > 65535:
            raise ValueError
    except IndexError:
        addr = '127.0.0.1'
        port = 7777
    except ValueError:
        print('Диапазон портов должен быть от 1024 до 65535')
        sys.exit(1)

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