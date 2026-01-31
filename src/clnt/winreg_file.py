"""
Ronny Getz
Read IP and port from constants (registry not used; kept for API).
"""
import winreg

from constants import IP, PORT

# Number of values returned by read_reg (ip, port)
VALUES_COUNT = 2


class Reg(object):
    """Provides read_reg returning (IP, PORT) from constants."""

    @staticmethod
    def read_reg():
        """Return (ip, port) from constants for server connection."""
        ip = IP
        port = PORT

        return ip, port
