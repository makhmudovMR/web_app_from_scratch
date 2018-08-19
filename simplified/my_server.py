import socket
from threading import Thread
from queue import Queue, Empty
from responses import *


class SimpleHTTPServer:

    def __init__(self, host="127.0.0.1", port=9001, worker_count=16):
        self.host = host
        self.port = port
        self.connection_queue = Queue()
        self.worker_count = worker_count
        self.connect_waiting = worker_count * 8


    def serve_forever(self):
        workers = []
        for _ in range(self.worker_count):
            worker = SimpleHTTPWorker(self.connection_queue)
            worker.start()
            workers.append(worker)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(self.connect_waiting)
            print(f"Listening {self.host}:{self.port}")

            while True:
                try:
                    self.connection_queue.put(sock.accept())
                except KeyboardInterrupt:
                    break


        for worker in workers:
            worker.stop()

        for worker in workers:
            worker.join()




class SimpleHTTPWorker(Thread):

    def __init__(self, connection_queue):
        super().__init__()
        self.connection_queue = connection_queue
        self.running = False
        pass


    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                client_sock, client_addr = self.connection_queue.get()
            except Empty:
                continue

            self.handle_client(client_sock, client_addr)

    def handle_client(self, client_sock, client_addr):
        """data = b""
        while True:
            data += client_sock.recv(1024)
            if not data:
                break

            print(data)"""
        client_sock.send(RESPONSE)




server = SimpleHTTPServer()
server.serve_forever()