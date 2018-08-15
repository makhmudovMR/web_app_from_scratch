import typing
from collections import defaultdict


class Headers:

    def __init__(self) -> None:
        self._headers = defaultdict(list)

    def add(self, name: str, value: str):
        self._headers[name.lower()].append(value)

    def get_all(self, name:str):
        return self._headers[name.lower()]

    def get(self, name: str, default: typing.Optional[str] = None) -> typing.Optional[str]:
        try:
            return self.get_all(name)[-1]
        except:
            return default


# header = Headers()
# header.add('height', '185')
# header.add('weight', '70kg')
#
# print(header._headers)
# print(header.get_all('height'))
# print(header.get_all('weight'))