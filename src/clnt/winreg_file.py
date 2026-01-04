"""
Ronny Getz
winreg
"""

#import winreg

from constants import IP, PORT

VALUES_COUNT = 2


class Reg(object):
    @staticmethod
    def read_reg():
        """
        gets the ip and the port from registry
        """
        #ip = IP
        #port = PORT

        #RawKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
        #                         r"SOFTWARE\\Technician Server")
        #for i in range(VALUES_COUNT):
        #    try:
        #        name, value, type = winreg.EnumValue(RawKey, i)
        #        if name == "IP":
        #            ip = value
        #        if name == "port":
        #            port = value
        #            print(i, name, value, type)
        #    except EnvironmentError:
        #        print("You have ", i, " values")
        #        break
        #winreg.CloseKey(RawKey)
        #return ip, port
        return IP, PORT
