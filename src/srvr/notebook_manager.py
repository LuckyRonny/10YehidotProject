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
    def GET_NOTEBOOK(params):
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
    def ADD_NOTEBOOK(params):
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
    def ADD_STROKE(params):
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
    def DELETE_STROKE(params):
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
    def CHANGE_BACKGROUND(params):
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
    def CLEAR(params):
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
    def ADD_PAGE(params):
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
    def CHECK_UPDATES(params):
        """adds a stroke to the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        time_stamp = params[1]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        NotebookManager.lock.release()
        if str(time_stamp) < str(notebook_db[name]["last_change"]):
            return NotebookManager.GET_NOTEBOOK(params)
        else:
            return "NO"

    @staticmethod
    def ADD_STROKES(params):
        """adds a stroke to the notebook from the db"""
        name = params[NAME]
        id_page = params[1]
        stroke_dict = ast.literal_eval(params[2])
        for s in stroke_dict:
            NotebookManager.ADD_STROKE([name, repr(stroke_dict[s]), id_page, s,
                                        20])
        return "ok"

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

    @staticmethod
    def GET_NEXT_STROKE_ID(params):
        """gets the next stroke id from the notebook from the db"""
        NotebookManager.lock.acquire()
        name = params[NAME]
        page_id = params[1]
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        next_stroke_id = notebook_db[name]["pages"][page_id]["stroke_id"]
        notebook_db[name]["pages"][page_id]["stroke_id"] = next_stroke_id + 1
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.lock.release()
        return next_stroke_id
