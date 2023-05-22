import json
import sys


def get_message(client):
    encoded = client.recv(1024)
    if isinstance(encoded, bytes):
        json_response = encoded.decode('utf-8')
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    if not isinstance(message, dict):
        raise ValueError
    json_msg = json.dumps(message)
    encoded_msg = json_msg.encode('utf-8')
    sock.send(encoded_msg)
    