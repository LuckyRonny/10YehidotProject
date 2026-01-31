"""
Ronny Getz
server
"""

import socket
import sys
import threading
import key_exchange
import methods
import protocol
from constants import (
    HAVE_PARAMETERS,
    IP,
    PARAMETERS,
    PORT,
    REQUEST,
    REQUEST_TYPE,
)


NUMBER_OF_CLIENTS = 1
UPDATES_PORT_OFFSET = 1


class Server(object):
    def __init__(self, ip, port):
        """
        gets an ip and a port and creates a socket and binds and listens
        and returns the socket
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET,
                                               socket.SOCK_STREAM)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(NUMBER_OF_CLIENTS)
            self.update_socket = socket.socket(socket.AF_INET,
                                               socket.SOCK_STREAM)
            self.update_socket.bind((ip, port + UPDATES_PORT_OFFSET))
            self.update_socket.listen(NUMBER_OF_CLIENTS)
        except socket.error as msg:
            print("Connection failure: %s\n terminating program" % msg)
            sys.exit(1)

    def handle_clients(self):
        """Accept clients on main socket
         spawn thread per client and start updates acceptor."""
        done = False
        while not done:
            try:
                client_socket, address = self.server_socket.accept()
                key = key_exchange.KeyExchange.recv_send_key((client_socket,
                                                              None))
                connection = (client_socket, key)
                clnt_thread = threading.Thread(
                    target=self.handle_single_client,
                    args=(connection, address))
                clnt_thread.start()
                threading.Thread(
                    target=self.accept_updates,
                    daemon=True
                ).start()
            except socket.error:
                print("socket error")

    def accept_updates(self):
        """Accept connections on updates socket; spawn thread per client."""
        while True:
            try:
                socket_updates, address = self.update_socket.accept()
                key = key_exchange.KeyExchange.recv_send_key((socket_updates,
                                                              None))
                connection_update = (socket_updates, key)
                clnt_thread = threading.Thread(
                    target=self.handle_update_client,
                    args=(connection_update, address))
                clnt_thread.start()
            except socket.error:
                print("update socket error")

    @staticmethod
    def handle_single_client(conn, address):
        """Loop: receive request, dispatch to Methods, send response
         stop on error."""
        done = False
        while not done:
            try:
                request, params = Server.receive_client_request(conn)
                response = Server.handle_client_request(request, params)
                Server.send_response_to_client(response, conn)
            except socket.error as msg:
                print("Server Error: ", msg)
                done = True
            except Exception as msg:
                print("Client request error: ", msg)
                done = True
        return False

    @staticmethod
    def handle_update_client(conn_updates, address):
        """Serve only CHECK_UPDATES; respond NO to other requests
         stop on error."""
        done = False
        while not done:
            try:
                request, params = Server.receive_client_request(conn_updates)
                if request != "CHECK_UPDATES":
                    Server.send_response_to_client("NO", conn_updates)
                    continue
                response = Server.handle_client_request(request, params)
                Server.send_response_to_client(response, conn_updates)
            except socket.error as msg:
                print("Update client error:", msg)
                done = True
            except Exception as msg:
                print("Update request error:", msg)
                done = True

    @staticmethod
    def receive_client_request(conn):
        """Receive one message; return
        (request_upper, params_list) or (None, None)."""
        request = protocol.Protocol.recv(conn)
        if request == "":
            return None, None
        req_and_prms = request.split("$")
        if len(req_and_prms) > HAVE_PARAMETERS:
            return req_and_prms[REQUEST].upper(), req_and_prms[PARAMETERS:]
        else:
            return req_and_prms[REQUEST].upper(), None

    @staticmethod
    def handle_client_request(request, params):
        """Dispatch to Methods by params[REQUEST_TYPE]; return response."""
        cls = getattr(methods, "Methods")
        return (getattr(cls, params[REQUEST_TYPE])
                (request, params))

    @staticmethod
    def send_response_to_client(response, conn):
        """Send response string over connection via Protocol.send."""
        protocol.Protocol.send(conn, response)


def main():
    """Create server on IP:PORT and run handle_clients (blocking)."""
    server = Server(IP, PORT)
    server.handle_clients()


if __name__ == "__main__":
    main()
