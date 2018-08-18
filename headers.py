from collections import defaultdict


class Headers:
    """
    Header will have a request parameters and properties
    """
    def __init__(self):
        self._headers = defaultdict(list)

    def add(self, name, value):
        self._headers[name.lower()].append(value)

    def get_all(self, name):
        return self._headers[name.lower()]

    def get(self, name, default):
        try:
            return self.get_all(name)[-1]
        except IndexError:
            return default

    def get_n(self, name, n):
        try:
            return self.get_all(name)[-n:]
        except IndexError:
            return self._headers[name.lower]

    def __iter__(self):
        for name, values in self._headers.items():
            for value in values:
                yield name, value

"""
o = Headers()
print(o._headers)
o._headers["key1"].append(5)
o._headers["key1"].append(2)
o._headers["key2"].append(2)
print(o._headers)
print(o._headers["key1"])
print(o._headers.items())

print("------------")

for i in o:
    print(i)
"""