import io
import typing
import socket

from headers import Headers


''' Просто читает и возвращает тело запроса, описание этого класса уточним позже'''
class BodyReader(io.IOBase):

    def __init__(self, sock, buff, bufsize=1024):
        self._sock = sock
        self._buff = buff
        self._bufsize = bufsize

    def readable(self):
        return True

    def read(self, n):
        while len(self._buff) < n:
            data = self._sock.recv(self._bufsize)
            if not data:
                return b""

            self._bufsize += data
        res , self._buff = self._buff[:n], self._buff[n:]
        return res



'''Класс который олицетворяет собойо запрос(HTTP запрос)'''
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