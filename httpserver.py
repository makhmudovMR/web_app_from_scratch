import socket
import typing
from request import Request
from request import BodyReader
from response import Response
from somefile1 import serve_file


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=9000) -> None:
        self.host = host
        self.port = port

    def serve_forever(self) -> None:
        with socket.socket() as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(0)
            print(f"Listening on {self.host}:{self.port}...")

            while True:
                client_sock, client_addr = server_sock.accept()
                self.handle_client(client_sock, client_addr)

    def handle_client(self, client_sock: socket.socket, client_addr: typing.Tuple[str, int]) -> None:
        with client_sock:
            try:
                print(f"New connection {client_addr}")
                request = Request.from_socket(client_sock)
                if "100-continue" in request.headers.get("expect", ""):
                    response = Response(status="100 Continue")
                    response.send(client_sock)

                try:
                    content_length = int(request.headers.get("content-length", "0"))
                except ValueError:
                    content_length = 0

                if content_length:
                    body = request.body.read(content_length)
                    print("Request body", body)

                if request.method != "GET":
                    response = Response(status="405 Method Not Allowed", content="Method Not Allowed")
                    response.send(client_sock)
                    return

                serve_file(client_sock, request.path)
            except Exception as e:
                print(f"Failed to parse request: {e}")
                response = Response(status="400 Bad Request", content="Bad Request")
                response.send(client_sock)


server = HTTPServer()
server.serve_forever()
