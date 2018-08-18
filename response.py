import io
import os
import socket
import typing

from headers import Headers


class Response:

    def __init__(self, status, headers, body, content, encoding = "utf-8"):
        self.status = status.encode()
        self.headers = headers or Headers()
        if content is not None:
            self.body = io.BytesIO(content.encode(encoding))
        elif body is None:
            self.body = io.BytesIO()
        else:
            self.body = body

    def send(self, sock):
        content_length = self.headers.get("content-length")

        if content_length is None:
            try:
                body_stat = os.fstat(self.body.fileno())
                content_length = body_stat.st_size
            except:
                """?"""
                self.body.seek(0, os.SEEK_END)
                content_length = self.body.tell()
                self.body.seek(0, os.SEEK_SET)
                """?"""

            if content_length > 0:
                self.headers.add("content-length", content_length)

        headers = b"HTTP/1.1 " + self.status + b"\r\n"
        for header_name, header_value in self.headers:
            headers += f"{header_name}: {header_value}\r\n".encode()

        sock.sendall(headers + b"\r\n")
        if content_length > 0:
            sock.sendfile(self.body)