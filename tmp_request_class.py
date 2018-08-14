import typing
import socket
from service import iter_lines


class Request(typing.NamedTuple):

    method: str
    path: str
    headers: typing.Mapping[str, str]

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


        headers = {}

        for line in lines:
            try:
                name, _, value = line.decode("ascii").partition(":")
                headers[name.lower()] = value.lstrip()
            except ValueError:
                raise ValueError(f"Недопустимая строка заголовка {line}")
        return cls(method=method.upper(), path=path, headers=headers)