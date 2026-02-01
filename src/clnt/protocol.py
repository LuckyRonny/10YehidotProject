"""
Ronny Getz
Client protocol: length-prefixed, optionally encrypted send/recv.
"""
import logging

from constants import MSG_LEN
from aes_cipher import AESCipher

# Connection tuple indices and recv loop sentinel
STOP_RECV = 0
KEY = 1
SOCK = 0


class Protocol(object):
    @staticmethod
    def send(conn, data):
        """Send string as length-prefixed payload; encrypt if conn has key."""
        data_bit = data.encode()
        if conn[KEY] is not None:
            data_bit = AESCipher.encrypt(conn[KEY], data_bit)
        length = len(data_bit)
        length_str = str(length)
        length_bit = length_str.zfill(MSG_LEN).encode()
        conn[SOCK].send(length_bit + data_bit)

    @staticmethod
    def send_bin(conn, data_bit):
        """Send raw bytes with length prefix; encrypt if conn has key."""
        if conn[KEY] is not None:
            data_bit = AESCipher.encrypt(conn[KEY], data_bit)
        length = len(data_bit)
        length_str = str(length)
        length_bit = length_str.zfill(MSG_LEN).encode()
        conn[SOCK].send(length_bit + data_bit)

    @staticmethod
    def recv(conn):
        """
        get the data from the socket until all the data get to the socket
        """
        data_len = b""
        data = b""
        length = MSG_LEN
        while length > STOP_RECV:
            data_len += conn[SOCK].recv(length)
            length = MSG_LEN - len(data_len)
        data_len = data_len.decode()
        if data_len.isdigit():
            total_size = int(data_len)
            while len(data) < total_size:
                remaining = total_size - len(data)
                chunk = conn[SOCK].recv(remaining)
                if not chunk:
                    break
                data += chunk
        if conn[KEY] is not None:
            data = AESCipher.decrypt(conn[KEY], data)
        return data.decode()

    @staticmethod
    def recv_bin(conn):
        """Read length-prefixed payload and return raw bytes
         decrypt if key set."""
        data = b""
        data_len = b""
        length = MSG_LEN
        while length > STOP_RECV:
            data_len += conn[SOCK].recv(length)
            length = MSG_LEN - len(data_len)
        data_len = data_len.decode()
        if data_len.isdigit():
            total_size = int(data_len)
            while len(data) < total_size:
                remaining = total_size - len(data)
                chunk = conn[SOCK].recv(remaining)
                if not chunk:
                    break
                data += chunk
        if conn[KEY] is not None:
            data = AESCipher.decrypt(conn[KEY], data)
        return data
