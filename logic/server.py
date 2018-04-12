#!/usr/bin/python3

from websocket_server import WebsocketServer
import json

# Called for every client connecting (after handshake)
def new_client(client, server):
	print("New client connected and was given id %d" % client['id'], flush=True)
	message = json.dumps({'x': 15, 'y': 30, 'type': 'absolute'})
	server.send_message_to_all(message)


# Called for every client disconnecting
def client_left(client, server):
	print("Client(%d) disconnected" % client['id'], flush=True)


# Called when a client sends a message
def message_received(client, server, message):
	#if len(message) > 200:
	#	message = message[:200]+'..'
	#server.send_message_to_all("Client(%d) said: %s" % (client['id'], message))
	contents = json.loads(message)
	print(contents, flush=True)
	server.send_message_to_all(message)

PORT=9001
server = WebsocketServer(PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
