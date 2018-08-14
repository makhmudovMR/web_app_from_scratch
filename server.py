import socket
import service
from request_class import Request
from responses import *


HOST = "127.0.0.1"
PORT = 9000


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    '''
    Bind the host and port to our server.
    0 is the number of pending connections the socket may have before new connections are refused.
    '''
    server_sock.bind((HOST, PORT))
    server_sock.listen(0)
    print(f"Listening on {HOST}:{PORT}...")

    # infinitely take new link
    while True:
        '''Take the clinet link'''
        client_sock, client_addr = server_sock.accept()
        print(f"New connection from {client_addr}.")
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
                print(request)
                client_sock.sendall(NOT_FOUND_RESPONSE)
            except Exception as e:
                print(f"Failed to parse request: {e}")
                client_sock.sendall(BAD_REQUEST_RESPONSE)