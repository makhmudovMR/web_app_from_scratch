import typing
import socket
from service import iter_lines
from headers import Headers
from bodyreader_class import BodyReader


class Request:
    '''
    This class must be understanded
    '''

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