import keyring
from easyrsa import *
from omnitools import *
from aescipher import *


__ALL__ = ["Broker"]


class Broker(object):
    def __init__(self, app_name: str, username: str) -> None:
        self.__split_length = 10 ** 3
        self.__app_name = app_name
        self.__username = username
        if len(self.__get()) == 0:
            self.set("", "")

    @staticmethod
    def __check() -> bool:
        import inspect
        if not inspect.stack()[2][1].replace("\\", ".").replace("/", ".").endswith("site-packages.credsafe.broker.py"):
            raise Exception("call outside Broker() is prohibited")
        return True

    def __get(self) -> Dict[str, str]:
        self.__check()
        v = ""
        i = 0
        while True:
            _ = keyring.get_password(sha512(f"{self.__app_name}[{i}]"), self.__username)
            if _ is None:
                break
            else:
                v += _
                i += 1
        if v == "":
            return {}
        return jl(b64d_and_utf8d(v))

    def get(self, k: str) -> str:
        return self.__get()[k]

    def __set(self, v: Dict[str, str]) -> bool:
        self.__check()
        v = b64e(jd(v))
        i = 0
        while v:
            keyring.set_password(sha512(f"{self.__app_name}[{i}]"), self.__username, v[:self.__split_length])
            v = v[self.__split_length:]
            i += 1
        return self.__delete(i)

    def set(self, k: str, v: str) -> bool:
        _ = self.__get()
        _[k] = v
        return self.__set(_)

    def rm(self, k: str) -> bool:
        _ = self.__get()
        _.pop(k)
        return self.__set(_)

    def __delete(self, i: int = 0) -> bool:
        self.__check()
        while True:
            kr = (sha512(f"{self.__app_name}[{i}]"), self.__username)
            _ = keyring.get_password(*kr)
            if _ is None:
                return True
            else:
                keyring.delete_password(*kr)
                i += 1

    def destroy(self) -> bool:
        self.__delete()
        self.__username = None
        self.__app_name = None
        return True



