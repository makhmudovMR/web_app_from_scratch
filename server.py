import mimetypes
import os
import socket
import typing

from request import Request
from response import Response
from threading import Thread
from queue import Queue, Empty



SERVER_ROOT = "www"


def serve_file(sock, path):
    """
    Находит файл на сервере и отправляет его клиенту
    :param sock:
    :param path:
    :return:
    """

    if path == "/":
        path = "index.html"

    """Формируем абстрактный путь к директории www"""
    abspath = os.path.normpath(os.path.join(SERVER_ROOT, path.lstrip("/")))
    if not abspath.startswith(SERVER_ROOT):
        response = Response(status="404 Not Found", content="Not Found")
        response.send(sock)
        return

    try:
        with open(abspath, "rb") as f:
            content_type, encoding = mimetypes.guess_type(abspath)
            if content_type is None:
                content_type = "application/octet-stream"

            if encoding is not None:
                content_type += f"; chatset={encoding}"

            response = Response(status="200 OK", body=f)
            response.headers.add("content-type", content_type)
            response.send(sock)
            return
    except FileNotFoundError:
        response = Response(status="404 Not Found", content="Not Found")
        response.send(sock)
        return


class HTTPWorker(Thread):
    """
    Поток который принимает соединение и обрабатывает его
    """
    def __init__(self, connection_queue, handlers):
        super().__init__(daemon=True)

        self.handlers = handlers
        self.connection_queue = connection_queue
        self.running = False

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                client_sock, client_addr = self.connection_queue.get(timeout=1)
            except Empty:
                continue

            try:
                self.handle_client(client_sock, client_addr)
            except Exception as e:
                print(f"Unhandled error {e}")
                continue
            finally:
                self.connection_queue.task_done()

    def handle_client(self, client_sock, client_addr):
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
            except Exception:
                response = Response(status="400 Bad Request", content="Bad Request")
                response.send(client_sock)
                return

            if "100-continue" in request.headers.get("expect", ""):
                response = Response(status="100 Continue")
                response.send(client_sock)

            for path_prefix, handler in self.handlers:
                if request.path.startswith(path_prefix):
                    try:
                        request = request._replace(path=request.path[len(path_prefix):])
                        response = handler(request)
                        response.send(client_sock)
                    except Exception as e:
                        response = Response(status="500 Internal Server Error", content="Internal Error")
                        response.send(client_sock)
                    finally:
                        break
            else:
                response = Response(status="404 Not Found", content="Not Found")
                response.send(client_sock)


    """
    def handle_client(self, client_sock, client_addr):
        with client_sock:
            try:
                request = Request.from_socket(client_sock)
                if "100-continue" in request.headers.get("except", ""):
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
    """


class HTTPServer:

    def __init__(self, host="127.0.0.1", port=9000, worker_count=16):
        self.handlers = []
        self.host = host
        self.port = port
        self.worker_count = worker_count
        self.worker_backlog = worker_count * 8 # очередь слушателей server_sock.lisnet()
        self.connection_queue = Queue(self.worker_backlog)

    def mount(self, path_prefix, handler):
        self.handlers.append((path_prefix, handler))

    def serve_forever(self):
        workers = []
        for _ in range(self.worker_count):
            worker = HTTPWorker(self.connection_queue, self.handlers)
            worker.start()
            workers.append(worker)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind((self.host, self.port))
                server_sock.listen(self.worker_backlog)
                print(f"Listning on {self.host}:{self.port}...")

                """"""

                while True:
                    try:
                        self.connection_queue.put(server_sock.accept()) # принимаем соединение и вставляем его в очередь
                    except KeyboardInterrupt:
                        break

            for worker in workers:
                worker.stop()

            for worker in workers:
                worker.join(timeout=30)


def app(request):
    return Response(status="200 OK", content="Hello!")


server = HTTPServer()
server.mount("", app)
server.serve_forever()