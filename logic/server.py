#!/usr/bin/python3

from websocket_server import WebsocketServer
import json

clients = []

# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'], flush=True)
    clients.append(client)


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'], flush=True)


# Called when a client sends a message
def message_received(client, server, message):
    log = open('log.txt', 'a')
    if client['id'] == 1:
        # web interface sent message, so send to driver
        print(message, flush=True)
        log.write('From web to driver: ' + message + '\n')
        contents=json.loads(message)
        to_send=json.dumps({'x': int(contents['x']), 'y': int(contents['y']), 'type':contents['type']})
        server.send_message(clients[1], to_send)
    elif client['id'] == 2:
        # driver sent message, so send to web interface
        print(message, flush=True)
        log.write('From driver to web: ' + message + '\n')
        server.send_message(clients[0], message)


PORT=9001
server = WebsocketServer(PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
