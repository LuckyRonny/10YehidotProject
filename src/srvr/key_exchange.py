"""
Server/client key exchange:
send or receive DH public key and derive shared key.
"""
import protocol
from diffie_hellman import *


class KeyExchange(object):

    @staticmethod
    def send_recv_key(conn):
        """Send local DH public key, receive peer key,
        return derived shared key."""
        dh = DiffieHellman()
        protocol.Protocol.send_bin(conn,
                               dh.serialize_public_key())  # DH public key
        dh_key_bytes = protocol.Protocol.recv_bin(conn)  # DH public key
        dh_key = dh.deserialize_public_key(dh_key_bytes)

        key = dh.get_key(dh_key)
        return key

    @staticmethod
    def recv_send_key(conn):
        """Receive client DH key, send server DH key,
        return derived shared key."""
        dh_key_bytes = protocol.Protocol.recv_bin(conn)
        dh = DiffieHellman()
        dh_key = dh.deserialize_public_key(dh_key_bytes)
        protocol.Protocol.send_bin(conn, dh.serialize_public_key())
        key = dh.get_key(dh_key)
        return key




