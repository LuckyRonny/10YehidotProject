"""
Ronny Getz
winreg
"""

import winreg

from constants import IP, PORT

VALUES_COUNT = 2


class Reg(object):
    @staticmethod
    def read_reg():
        """
        gets the ip and the port from registry
        """
        ip = IP
        port = PORT

        return ip, port
