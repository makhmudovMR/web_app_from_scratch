import socket
from request_class import Request
HOST = '127.0.0.1'
PORT = 9000


RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 15

<h1>Hello!</h1>""".replace(b"\n", b"\r\n")

with socket.socket() as server_sock:

    # server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(0)
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"New connection from {client_addr}.")
        with client_sock:
            request = Request.from_socket(client_sock) # грубо говоря получаем имформацию о клиенте в более структурированном виде
            print(request)
            client_sock.sendall(RESPONSE)
