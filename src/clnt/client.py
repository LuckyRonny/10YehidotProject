"""
Ronny Getz
client
"""

import socket
import sys

import protocol
from constants import *
import winreg_file
import methods

NO_PARAMETERS = 0
PARAMETER = 1
TWO_PARAMETERS = 2


class Client(object):
    def __init__(self):
        """
        constructor - gets an ip and port and create a socket
        and return the socket
        """
        try:
            ip, port = winreg_file.Reg.read_reg()
            self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.my_socket.connect((ip, port))
        except socket.error as msg:
            print("Connection failure: %s\n terminating program" % msg)
            sys.exit(1)

    def handle_user_input(self):
        """
        gets a socket and while request is not EXIT or QUIT
        the function ask for request and checks if it is legal and
        call the functions send_request_to_server and handle_server_response
        """
        try:
            request = None
            while request != "EXIT" and request != "QUIT":
                request = input("please enter a request ").upper()
                if self.valid_request(request):
                    self.send_request_to_server(request)
                    if request == "RELOAD":
                        methods.Methods.send_file("methods.py",
                                                  self.my_socket)
                    self.handle_server_response(request)
                else:
                    print("illegal request")
        except socket.error as msg:
            print("handle_user_input - socket error:", msg)
        except Exception as msg:
            print("handle_user_input - general error:", msg)

    @staticmethod
    def valid_request(request):
        """
        gets a request and checks if the request legal
        and if the number of parameters is legal
        """
        req_and_prms = request.split()
        if (req_and_prms[REQUEST] == "EXIT" and
                len(req_and_prms[PARAMETERS:]) == NO_PARAMETERS or
                req_and_prms[REQUEST] == "QUIT" and
                len(req_and_prms[PARAMETERS:]) == NO_PARAMETERS or
                req_and_prms[REQUEST] == "TAKE_SCREENSHOT" and
                len(req_and_prms[PARAMETERS:]) == NO_PARAMETERS or
                req_and_prms[REQUEST] == "DIR" and
                len(req_and_prms[PARAMETERS:]) == PARAMETER or
                req_and_prms[REQUEST] == "DELETE" and
                len(req_and_prms[PARAMETERS:]) == PARAMETER or
                req_and_prms[REQUEST] == "COPY" and
                len(req_and_prms[PARAMETERS:]) == TWO_PARAMETERS or
                req_and_prms[REQUEST] == "EXECUTE" and
                len(req_and_prms[PARAMETERS:]) == PARAMETER or
                req_and_prms[REQUEST] == "SEND_FILE" and
                len(req_and_prms[PARAMETERS:]) == PARAMETER or
                req_and_prms[REQUEST] == "RELOAD" and
                len(req_and_prms[PARAMETERS:]) == NO_PARAMETERS or
                req_and_prms[REQUEST] == "HISTORY" and
                len(req_and_prms[PARAMETERS:]) == NO_PARAMETERS):
            return True
        return False

    def send_request_to_server(self, request):
        """
        gets a socket and a request and sent it to the server
        """
        protocol.Protocol.send(self.my_socket, request)

    def handle_server_response(self, request):
        """
        gets a socket and gets a data from the server and prints it
        """
        req_and_prms = request.split()
        if req_and_prms[REQUEST] == "SEND_FILE":
            methods.Methods.receive_file_request(request, self.my_socket)
            data = protocol.Protocol.recv(self.my_socket)
        else:
            data = protocol.Protocol.recv(self.my_socket)
        return data  # returns string

    def send_command(self, request):
        """
        gets a request and checks if it is legal and
        call the functions send_request_to_server and
        handle_server_response and return the response
        """
        rsp = ""
        if self.valid_request(request):
            self.send_request_to_server(request)
            rsp = self.handle_server_response(request)
        else:
            rsp = "ILLEGAL REQUEST"
        return rsp


def main():
    """
    construct a client and runs it
    """
    client = Client()
    client.handle_user_input()


if __name__ == "__main__":
    main()
