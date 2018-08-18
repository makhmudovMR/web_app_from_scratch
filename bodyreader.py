import io


class BodyReader(io.IOBase):

    def __init__(self, sock, buff, bufsize):
        self._sock = sock
        self._buff = buff
        self._bufsize = bufsize

    def readable(self):
        return True

    def read(self, n):
        while len(self._buff) < n:
            data = self._sock.recv(self._bufsize)
            if not data:
                break

            self._buff += data

        res, self._buff = self._buff[:n], self._buff[n:]
        return res