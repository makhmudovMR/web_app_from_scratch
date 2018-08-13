import socket
from request_class import Request
from file_server import iter_lines


HOST = '127.0.0.1'
PORT = 9000

''' Формируем ответ'''
RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 30

<h1>Hello! It's Server</h1>""".replace(b"\n", b"\r\n")


'''Формируем овтет ошибки'''
BAD_REQUEST_RESPONSE = b"""\
HTTP/1.1 400 Bad Request
Content-type: text/plain
Content-length: 11

Bad Request""".replace(b"\n", b"\r\n")

with socket.socket() as server_sock:
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(0)
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"Received connection from {client_addr}...")
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
                print(request)
                client_sock.sendall(RESPONSE)
            except Exception as e:
                print(f"Failed to parse request: {e}")
                client_sock.sendall(BAD_REQUEST_RESPONSE)