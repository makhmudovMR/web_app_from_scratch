import io
import typing
import socket
from headers import Headers
from bodyreader import BodyReader



'''Класс который олицетворяет собой запрос(HTTP запрос)'''
class Request:

    def __init__(self, *args, **kwargs):
        self.method = kwargs['method']
        self.path = kwargs['path']
        self.headers = kwargs['headers']
        self.body = kwargs['body']

    @classmethod
    def from_socket(cls, sock: socket.socket) -> "Request":
        lines = iter_lines(sock)

        try:
            request_line = next(lines).decode("ascii")
        except StopIteration:
            raise ValueError("Отсутствует строка запроса")


        try:
            method, path, _ = request_line.split(" ") # первая строка http заголовка example (GET HTTP/1.1 ....)
        except ValueError:
            raise ValueError(f"Недопустимая строка  {request_line}")


        headers = Headers()
        buff = b""

        while True:
            try:
                line = next(lines)
            except StopIteration as e:
                # StopIteration.value contains the return value of the generator.
                buff = e.value
                break

            try:
                name, _, value = line.decode("ascii").partition(":")
                headers.add(name, value.lstrip())
            except ValueError:
                raise ValueError(f"Malformed header line {line!r}.")

        body = BodyReader(sock, buff=buff)
        return cls(method=method.upper(), path=path, headers=headers, body=body)



'''Эта функция возвращает итератор со строками HTTP запроса'''


def iter_lines(sock, buff_size=1024):
    buff = b""
    while True:
        data = sock.recv(buff_size)
        if not data:
            return b""

        buff += data

        while True:
            try:
                i = buff.index(b"\r\n")
                line, buff = buff[:i], buff[i+2:]

                if not line:
                    return buff

                yield line
            except IndexError:
                break