"""
Ronny Getz
protocol server
"""
from constants import MSG_LEN
from aes_cipher import *
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='client.log', encoding='utf-8', level=logging.DEBUG)
logger.info('Starting the logger on file "client.log"')

STOP_RECV = 0
KEY = 1
SOCK = 0


class Protocol(object):
    @staticmethod
    def send(conn, data):
        """
        send the data to the socket with the length of the data at the start
        """
        data_bit = data.encode()
        if conn[KEY] is not None:
            data_bit = AESCipher.encrypt(conn[KEY], data_bit)
        length = len(data_bit)
        length_str = str(length)
        length_bit = length_str.zfill(MSG_LEN).encode()
        logger.debug(f"Sending {data_bit[:80]} ... to socket {conn[SOCK]}")
        conn[SOCK].send(length_bit + data_bit)

    @staticmethod
    def send_bin(conn, data_bit):
        """
        send the data to the socket with
        the length of the data at the start in bytes
        """
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
        logger.debug(f"Received message: {data[:80]} ... from socket {conn[SOCK]}")
        if conn[KEY] is not None:
            data = AESCipher.decrypt(conn[KEY], data)
        return data.decode()

    @staticmethod
    def recv_bin(conn):
        """
        get the data from the socket until
        all the data get to the socket in bytes
        """
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
