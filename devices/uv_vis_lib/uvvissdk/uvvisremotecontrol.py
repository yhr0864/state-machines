import ctypes
from collections import namedtuple

import _uvvisloadlib

uvvis_api = _uvvisloadlib.load_lib("SpecDLL")


class Uvvis:
    def __init__(self, handle=ctypes.c_longlong()):
        super().__init__(handle)

    def test_lib(self):
        result = uvvis_api.LibTest()
        return result


if __name__ == "__main__":
    uvvis = Uvvis()
    print(uvvis.test_lib())
