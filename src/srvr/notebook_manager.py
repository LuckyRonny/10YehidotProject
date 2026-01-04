"""
Ronny Getz
Notebook manager server
"""

import ast
import json
import threading

from constants import NAME, NOTE_BOOK


class NotebookManager(object):
    lock = threading.Lock()
    @staticmethod
    def GET_NOTEBOOK(params, socket, address):
        """
        gets the notebook from the db
        """
        name = params[NAME]
        NotebookManager.lock.acquire()
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook = notebook_db[name]
        NotebookManager.lock.release()
        return repr(notebook)

    @staticmethod
    def ADD_NOTEBOOK(params, socket, address):
        """adds the notebook to the db"""
        name = params[NAME]
        notebook = ast.literal_eval(params[NOTE_BOOK])
        NotebookManager.lock.acquire()
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
        name = params[NAME]
        stroke = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[2]
        id = params[3]
        if id == "0":
            id = NotebookManager.GET_STROKE_ID([name, id_page])
            stroke["id"] = id
        NotebookManager.lock.acquire()
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id_page]["strokes"][id] = stroke
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, float(params[4]) + 1.0)
        return "ok"

    @staticmethod
    def DELETE_STROKE(params, socket, address):
        """adds a stroke to the notebook from the db"""
        name = params[NAME]
        id_page = params[1]
        id = params[2]
        NotebookManager.lock.acquire()
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
        name = params[NAME]
        id_page = params[1]
        page_type = params[2]
        NotebookManager.lock.acquire()
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        notebook_db[name]["pages"][id_page]["page_type"] = page_type
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.CHANGE_TIME_STAMP(name, params[3])
        return "ok"

    @staticmethod
    def CLEAR(params, socket, address):
        """clears the strokes of the notebook from the db"""
        name = params[NAME]
        id = params[1]
        NotebookManager.lock.acquire()
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
        name = params[NAME]
        page = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[2]
        NotebookManager.lock.acquire()
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
        name = params[NAME]
        time_stamp = params[1]
        NotebookManager.lock.acquire()
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        NotebookManager.lock.release()
        if float(time_stamp) < float(notebook_db[name]["last_change"]):
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

    @staticmethod
    def GET_STROKE_ID(params):
        """gets the next stroke id from the notebook from the db"""
        name = params[NAME]
        page_id = params[1]
        NotebookManager.lock.acquire()
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        next_stroke_id = notebook_db[name]["pages"][page_id]["stroke_id"]
        print(f"Next Stroke is: ={next_stroke_id}=")
        temp = str(int(next_stroke_id) + 1)
        print(f"New Stroke is: ={next_stroke_id}= , Next stroke will be ={temp}=")
        notebook_db[name]["pages"][page_id]["stroke_id"] = temp
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        NotebookManager.lock.release()
        return next_stroke_id
