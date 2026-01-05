"""
Ronny Getz
protocol server
"""
from constants import MSG_LEN

STOP_RECV = 0


class Protocol(object):
    @staticmethod
    def send(socket, data):
        """
        send the data to the socket with the length of the data at the start
        """
        data_bit = data.encode()
        length = len(data_bit)
        length_str = str(length)
        length_bit = length_str.zfill(MSG_LEN).encode()
        socket.send(length_bit + data_bit)

    @staticmethod
    def send_bin(socket, data_bit):
        """
        send the data to the socket with
        the length of the data at the start in bytes
        """
        length = len(data_bit)
        length_str = str(length)
        length_bit = length_str.zfill(MSG_LEN).encode()
        socket.send(length_bit + data_bit)

    @staticmethod
    def recv(socket):
        """
        get the data from the socket until all the data get to the socket
        """
        data_len = b""
        data = b""
        length = MSG_LEN
        while length > STOP_RECV:
            data_len += socket.recv(length)
            length = MSG_LEN - len(data_len)
        data_len = data_len.decode()
        if data_len.isdigit():
            total_size = int(data_len)
            while len(data) < total_size:
                remaining = total_size - len(data)
                chunk = socket.recv(remaining)
                if not chunk:
                    break
                data += chunk
        return data.decode()

    @staticmethod
    def recv_bin(socket):
        """
        get the data from the socket until
        all the data get to the socket in bytes
        """
        data = b""
        data_len = b""
        length = MSG_LEN
        while length > STOP_RECV:
            data_len += socket.recv(length)
            length = MSG_LEN - len(data_len)
        data_len = data_len.decode()
        if data_len.isdigit():
            total_size = int(data_len)
            while len(data) < total_size:
                remaining = total_size - len(data)
                chunk = socket.recv(remaining)
                if not chunk:
                    break
                data += chunk
        return data
