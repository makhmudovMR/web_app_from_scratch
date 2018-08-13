import socket
import service


HOST = "127.0.0.1"
PORT = 9000


RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 15

<h1>Hello!</h1>""".replace(b"\n", b"\r\n")

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
            for request_line in service.iter_lines(client_sock):
                print(request_line)
            client_sock.sendall(RESPONSE)