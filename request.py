import typing
import socket
from headers import Headers
from bodyreader import BodyReader


def iter_lines(sock, bufsize):
    buff = b""
    while True:
        data = sock.recv(bufsize)
        if not data:
            break

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


class Request(typing.NamedTuple):

    method:str
    path:str
    headers:Headers
    body:BodyReader

    @classmethod
    def from_socket(cls, sock: socket.socket):
        lines = iter_lines(sock)

        try:
            request_line = next(lines).decode("ascii")
        except StopIteration:
            raise ValueError("Request line missing")

        try:
            method, path, _ = request_line.split(" ")
        except ValueError:
            raise ValueError(f"Malformed request line {request_line!r}.")

        headers = Headers()
        buff = b""

        while True:
            try:
                line = next(lines)
            except StopIteration as e:
                buff = e.value
                break

            try:
                name, _, value = line.decode("ascii").partition(":")
                headers.add(name, value.lstrip())
            except ValueError:
                raise ValueError(f"Malformed headers line {line!r}.")

        body = BodyReader(sock, buff=buff)
        return cls(method=method.upper(), path=path, headers=headers, body=body)