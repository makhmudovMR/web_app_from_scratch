import typing
import socket
from file_server import iter_lines


class Request:

    method = None
    path = None
    headers = None

    @classmethod
    def from_socket(cls, sock:socket.socket):
        lines = iter_lines(sock)
        try:
            request_line = next(lines).decode('ascii')
        except StopIteration:
            raise ValueError('Request line missing.')

        try:
            method, path, _ = request_line.split(" ")
        except ValueError:
            raise ValueError(f"Malformed request line {request_line!r}.")

        headers = {}

        for line in lines:
            try:
                name, _, value, = line.decode("ascii").partition(":")
                headers[name.lower()] = value.lstrip()
            except ValueError:
                raise ValueError(f"Malformed header line {line!r}.")
        return cls(method=method.upper(), path=path, headers=headers)