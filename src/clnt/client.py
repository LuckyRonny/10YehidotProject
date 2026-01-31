"""
Ronny Getz
client
"""

import socket
import sys

import protocol
import winreg_file
from constants import (
    ADD_NOTEBOOK_DB_PARAMS,
    ADD_NOTEBOOK_PARAMS,
    CLIENTS_NOTEBOOKS_PARAMS,
    GET_NOTEBOOK_PARAMS,
    LOGIN_PARAMS,
    PASSWORD,
    REQUEST,
    SIGNUP_PARAMS,
    USERNAME,
)

ADD_STROKE_PRMS = 6
DELETE_STROKE_PRMS = 5
CHANGE_BACKGROUND_PRMS = 5
CLEAR_PRMS = 4
ADD_PAGE_PRMS = 5
CHECK_UPDATES_PRMS = 4


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
            self.check_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.check_socket.connect((ip, port + 1))
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
                    self.handle_server_response(request)
                else:
                    print("illegal request")
        except socket.error as msg:
            print("handle_user_input - socket error:", msg)
        except Exception as msg:
            print("handle_user_input - general error:", msg)

    @staticmethod
    def valid_request(req_and_prms):
        """
        gets a request and checks if the request legal
        and if the number of parameters is legal
        """
        if (Client.login_check(req_and_prms) or
            Client.signup_check(req_and_prms) or
            Client.funcs_check(req_and_prms) or
            req_and_prms[REQUEST] == "add_notebook" and
                len(req_and_prms) == ADD_NOTEBOOK_PARAMS or
            req_and_prms[REQUEST] == "get_notebook" and
                len(req_and_prms) == GET_NOTEBOOK_PARAMS or
            req_and_prms[REQUEST] == "add_notebook_to_db" and
                len(req_and_prms) == ADD_NOTEBOOK_DB_PARAMS or
            req_and_prms[REQUEST] == "all_users" and
                len(req_and_prms) == 4 or
            req_and_prms[REQUEST] == "change_access" and
                len(req_and_prms) == 5 or
            req_and_prms[REQUEST] == "clients_notebooks" and
                len(req_and_prms) == CLIENTS_NOTEBOOKS_PARAMS):
            return True
        return False

    @staticmethod
    def login_check(req_and_prms):
        """login check if valid"""
        return (req_and_prms[REQUEST] == "login" and
                len(req_and_prms) == LOGIN_PARAMS and
                "--" not in req_and_prms[USERNAME] and
                ";" not in req_and_prms[USERNAME] and
                "--" not in req_and_prms[PASSWORD] and
                ";" not in req_and_prms[PASSWORD])

    @staticmethod
    def signup_check(req_and_prms):
        """signup check if valid"""
        return (req_and_prms[REQUEST] == "signup" and
                len(req_and_prms) == SIGNUP_PARAMS and
                "--" not in req_and_prms[USERNAME] and
                ";" not in req_and_prms[USERNAME] and
                "--" not in req_and_prms[PASSWORD] and
                ";" not in req_and_prms[PASSWORD])

    @staticmethod
    def funcs_check(req_and_prms):
        """notebooks check request"""
        return (req_and_prms[REQUEST] == "add_stroke" and
                len(req_and_prms) == ADD_STROKE_PRMS or
                req_and_prms[REQUEST] == "delete_stroke" and
                len(req_and_prms) == DELETE_STROKE_PRMS or
                req_and_prms[REQUEST] == "change_background" and
                len(req_and_prms) == CHANGE_BACKGROUND_PRMS or
                req_and_prms[REQUEST] == "clear" and
                len(req_and_prms) == CLEAR_PRMS or
                req_and_prms[REQUEST] == "add_page" and
                len(req_and_prms) == ADD_PAGE_PRMS or
                req_and_prms[REQUEST] == "check_updates" and
                len(req_and_prms) == CHECK_UPDATES_PRMS)

    def send_request_to_server(self, sock, request):
        """
        gets a socket and a request and sent it to the server
        """
        protocol.Protocol.send(sock, request)

    def handle_server_response(self, sock):
        """
        gets a socket and gets a data from the server and prints it
        """
        data = protocol.Protocol.recv(sock)
        return data  # returns string

    def send_command(self, request):
        """
        gets a request and checks if it is legal and
        call the functions send_request_to_server and
        handle_server_response and return the response
        """
        rsp = ""
        req_and_prms = request.split("$")
        if self.valid_request(req_and_prms):
            if req_and_prms[REQUEST] == "check_updates":
                self.send_request_to_server(self.check_socket, request)
                rsp = self.handle_server_response(self.check_socket)
            else:
                self.send_request_to_server(self.my_socket, request)
                rsp = self.handle_server_response(self.my_socket)
        else:
            rsp = "ILLEGAL REQUEST"
        return rsp
