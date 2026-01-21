"""
Ronny Getz
server
"""

import socket
import sys
import threading

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
            self.update_socket.bind((ip, port + 1))
            self.update_socket.listen(NUMBER_OF_CLIENTS)
        except socket.error as msg:
            print("Connection failure: %s\n terminating program" % msg)
            sys.exit(1)

    def handle_clients(self):
        """
        gets a socket and while done is not true the function
        call the function handle_single_client
        """
        done = False
        while not done:
            try:
                client_socket, address = self.server_socket.accept()
                clnt_thread = threading.Thread(
                    target=self.handle_single_client,
                    args=(client_socket, address))
                clnt_thread.start()
                threading.Thread(
                    target=self.accept_updates,
                    daemon=True
                ).start()
            except socket.error:
                print("socket error")

    def accept_updates(self):
        """accept clients for updates socket"""
        while True:
            try:
                client_socket, address = self.update_socket.accept()
                clnt_thread = threading.Thread(
                    target=self.handle_update_client,
                    args=(client_socket, address))
                clnt_thread.start()
            except socket.error:
                print("update socket error")

    @staticmethod
    def handle_single_client(client_socket, address):
        """
        gets a socket and while response is not QUIT or EXIT
        the function calls the functions receive_client_request,
        request_client_handle, send_response_to_client
        """
        done = False
        while not done:
            try:
                request, params = Server.receive_client_request(client_socket)
                response = Server.handle_client_request(request, params)
                Server.send_response_to_client(response, client_socket)
            except socket.error as msg:
                print("Server Error: ", msg)
                done = True
            except Exception as msg:
                print("Client request error: ", msg)
                done = True
        return False

    @staticmethod
    def handle_update_client(client_socket, address):
        """handle update requests from client"""
        done = False
        while not done:
            try:
                request, params = Server.receive_client_request(client_socket)
                if request != "CHECK_UPDATES":
                    Server.send_response_to_client("NO", client_socket)
                    continue
                response = Server.handle_client_request(request, params)
                Server.send_response_to_client(response, client_socket)
            except socket.error as msg:
                print("Update client error:", msg)
                done = True
            except Exception as msg:
                print("Update request error:", msg)
                done = True

    @staticmethod
    def receive_client_request(client_socket):
        """
        gets a socket and receives a request
        """
        request = protocol.Protocol.recv(client_socket)
        if request == "":
            return None, None
        req_and_prms = request.split("$")
        if len(req_and_prms) > HAVE_PARAMETERS:
            return req_and_prms[REQUEST].upper(), req_and_prms[PARAMETERS:]
        else:
            return req_and_prms[REQUEST].upper(), None

    @staticmethod
    def handle_client_request(request, params):
        """
        gets a request and check which request to do and
        call the function and returns the response
        """
        cls = getattr(methods, "Methods")
        return (getattr(cls, params[REQUEST_TYPE])
                (request, params))

    @staticmethod
    def send_response_to_client(response, client_socket):
        """
        gets a response and a socket and send the response to the socket
        """
        protocol.Protocol.send(client_socket, response)


def main():
    """
    calls the functions initiate_server_socket and handle_clients
    and then close the socket
    """
    server = Server(IP, PORT)
    server.handle_clients()


if __name__ == "__main__":
    main()
