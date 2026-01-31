"""
Ronny Getz
winreg
"""

from winreg import *
from constants import *

VALUES_COUNT = 2


class Reg(object):
    @staticmethod
    def read_reg():
        """
        gets the ip and the port from registry
        """
        ip = IP
        port = PORT

        RawKey = OpenKey(HKEY_LOCAL_MACHINE,
                         r"SOFTWARE\\Technition Server")
        for i in range(VALUES_COUNT):
            try:
                name, value, type = EnumValue(RawKey, i)
                if name == "IP":
                    ip = value
                if name == "port":
                    port = value
                print(i, name, value, type)
            except EnvironmentError:
                print("You have ", i, " values")
                break
        CloseKey(RawKey)
        return ip, port
