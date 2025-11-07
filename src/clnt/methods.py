"""
Ronny Gets
methods client
"""

import threading
from PIL import ImageGrab
import glob
import os
import shutil
import subprocess
import protocol
import importlib
import sys
from constants import *

FILE_SENT = "file sent"
RECEIVED_FILE_LOCATION = "c:\\test_folder\\client"
EXECUTED = "program executed"
FILE_COPIED = "file copied"
FILE_NOT_EXIST = "the file does not exist"
DELETE_FILE = "file deleted"
EXIT_SERVER = "exit"
QUIT_SERVER = "quit"
SCREENSHOT = "screenshot taken"
IMAGE_FILE = "c:\\test_folder\\server\\screen.jpg"


class Methods(object):
    hist = {}
    lock = threading.Lock()

    @staticmethod
    def new_hist(address):
        """
        insert new entry to dict
        """
        Methods.lock.acquire()
        Methods.hist[address] = []
        Methods.lock.release()

    @staticmethod
    def add_to_hist(address, request):
        """
        add a request to dict
        """
        Methods.lock.acquire()
        Methods.hist[address].append(request)
        Methods.lock.release()

    @staticmethod
    def EXIT(params, socket, address):
        """
        returns EXIT
        """
        return EXIT_SERVER

    @staticmethod
    def QUIT(params, socket, address):
        """
        returns QUIT
        """
        return QUIT_SERVER

    @staticmethod
    def TAKE_SCREENSHOT(params, socket, address):
        """
        take a screenshot and save it in server folder
        and return screenshot taken
        """
        im = ImageGrab.grab()
        im.save(IMAGE_FILE)
        return SCREENSHOT

    @staticmethod
    def DIR(params, socket, address):
        """
        gets a folder and returns the list of files in the folder
        """
        folder = params[FOLDER] + "\\*.*"
        files_list = glob.glob(folder)
        files = str(files_list)
        return files

    @staticmethod
    def DELETE(params, socket, address):
        """
        gets a file and deletes it and returns file deleted
        """
        os.remove(params[FILE])
        return DELETE_FILE

    @staticmethod
    def COPY(params, socket, address):
        """
        gets a file and a folder and copy the file to the folder
        """
        shutil.copy(params[FILE], params[COPY_TO_FOLDER])
        return FILE_COPIED

    @staticmethod
    def EXECUTE(params, socket, address):
        """
        gets a file and a folder and copy the file to the folder
        """
        subprocess.call(params[SOFTWARE])
        return EXECUTED

    @staticmethod
    def file_name(file):
        """
        gets a file and returns the file in the saved folder
        """
        list_file = file.split("\\")
        name = list_file[NAME_INDEX]
        answer_file = RECEIVED_FILE_LOCATION + "\\" + name
        return answer_file

    @staticmethod
    def receive_file(file_name, socket):
        """
        gets a file and a socket and receive data
        and write it in the file we created
        """
        done = False
        new_file = open(file_name, "wb")
        while not done:
            data = protocol.Protocol.recv_bin(socket)
            if data == EOF:     # end of file (when we receive -1)
                done = True
            else:
                new_file.write(data)
        new_file.close()

    @staticmethod
    def receive_file_request(request, socket):
        """
        gets a request and a socket and take the
        file from the request and creates a new file
        and calls to receive_file
        """
        request = request.split()
        answer_file = Methods.file_name(request[FILE_SEND_FILE])
        Methods.receive_file(answer_file, socket)

    @staticmethod
    def send_file(file_name, socket):
        """
        gets a file and a socket and read 1024 bytes
        and send it to the socket while it didn't get
        to the ens of the file
        """
        done = False
        file = open(file_name, "rb")
        while not done:
            data = file.read(CHUNK)
            if data == b"":  # the file ended
                protocol.Protocol.send_bin(socket, EOF)
                done = True
            else:
                protocol.Protocol.send_bin(socket, data)
        file.close()
        return FILE_SENT

    @staticmethod
    def SEND_FILE(params, socket, address):
        """
        gets parameters and a socket and takes the file
        name from the parameters and calls to send_file
        """
        name_file = params[FILE]
        return Methods.send_file(name_file, socket)

    @staticmethod
    def RELOAD(params, socket, address):
        """
        reloads the file methods.py in the server
        """
        Methods.receive_file("methods.py", socket)
        importlib.reload(sys.modules[__name__])
        return "module reloaded"

    @staticmethod
    def HISTORY(params, socket, address):
        """
        returns history for the given address
        """
        Methods.lock.acquire()
        history = str(Methods.hist[address])
        Methods.lock.release()
        return history
