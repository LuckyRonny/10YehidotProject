"""
Ronny Gets
notebook manager server
"""

import threading
import json
import ast
from constants import *


class NotebookManager(object):


    @staticmethod
    def GET_NOTEBOOK(params, socket, address):
        """
        """
        name = params[NAME]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook = notebook_db[name]
        return repr(notebook)


    @staticmethod
    def ADD_NOTEBOOK(params, socket, address):
        """

        """
        name = params[NAME]
        notebook = ast.literal_eval(params[NOTE_BOOK])
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name] = notebook
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        return "ok"