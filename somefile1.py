'''
serve_file находи файл указанный в пути, пытается определить его mimetype и отправляет
загаловки и файл в случае если файл существует
иначе он отправляет запрос Not Found
'''


import mimetypes
import os
import socket
import typing
from responses import *

# we get this: (C:\python_projects\web_app_from_scratch\www)
SERVER_ROOT = os.path.abspath("www") # ?
print('this is server root:', SERVER_ROOT)


def serve_file(sock: socket.socket, path: str) -> None:
    if path =="/":
        path = "/index.html"

    # we get it if path = '/' : (C:\python_projects\web_app_from_scratch\www\index.html)
    abspath = os.path.normpath(os.path.join(SERVER_ROOT, path.lstrip("/")))
    # print('this is abspath:', abspath)

    if not abspath.startswith(SERVER_ROOT):
        sock.sendall(NOT_FOUND_RESPONSE)
        return

    try:
        with open(abspath, 'rb') as f:
            stat = os.path(f.fileno())
            content_type, encoding = mimetypes.guess_type(abspath)
            if content_type is None:
                content_type = 'application/octet-stream'

            if encoding is not None:
                content_type += f"; charset={encoding}"

            response_headers = FILE_RESPONSE_TEMPLATE.format(
                content_type=content_type,
                content_length=stat.st_size,
            ).encode("ascii")

            sock.sendall(response_headers)
            sock.sendfile(f)
    except:
        sock.sendall(NOT_FOUND_RESPONSE)
        return