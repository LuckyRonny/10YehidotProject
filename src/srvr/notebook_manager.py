"""
Ronny Getz
Notebook manager server
"""

import json
import ast
import threading
from constants import *


class NotebookManager(object):
    lock = threading.Lock()
    @staticmethod
    def GET_NOTEBOOK(params, socket, address):
        """
        gets the notebook from the db
        """
        NotebookManager.lock.acquire()
        name = params[NAME]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook = notebook_db[name]
        NotebookManager.lock.release()
        return repr(notebook)

    @staticmethod
    def ADD_NOTEBOOK(params, socket, address):
        """adds the notebook to the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        notebook = ast.literal_eval(params[NOTE_BOOK])
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name] = notebook
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.lock.release()
        return "ok"

    @staticmethod
    def ADD_STROKE(params, socket, address):
        """adds a stroke to the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        stroke = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[2]
        id = params[3]
        stroke_id = params[4]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id_page]["strokes"][id] = stroke
        notebook_db[name]["pages"][id_page]["stroke_id"] = stroke_id
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, params[5])
        return "ok"

    @staticmethod
    def DELETE_STROKE(params, socket, address):
        """adds a stroke to the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        id_page = params[1]
        id = params[2]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id_page]["strokes"].pop(id)
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, params[3])
        return "ok"

    @staticmethod
    def CHANGE_BACKGROUND(params, socket, address):
        """change the background of the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        id_page = params[1]
        type = params[2]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id_page]["page_type"] = type
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, params[3])
        return "ok"

    @staticmethod
    def CLEAR(params, socket, address):
        """clears the strokes of the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        id = params[1]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id]["strokes"] = {}
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, params[2])
        return "ok"

    @staticmethod
    def ADD_PAGE(params, socket, address):
        """adds a stroke to the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        page = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[2]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id_page] = page
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, params[3])
        return "ok"

    @staticmethod
    def CHECK_UPDATES(params, socket, address):
        """adds a stroke to the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        time_stamp = params[1]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        NotebookManager.lock.release()
        if str(time_stamp) < str(notebook_db[name]["last_change"]):
            return NotebookManager.GET_NOTEBOOK(params, socket, address)
        else:
            return "NO"

    @staticmethod
    def CHANGE_TIME_STAMP(name, time_stamp):
        """adds a stroke to the notebook from the db"""
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["last_change"] = float(time_stamp)
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.lock.release()
        return "ok"
