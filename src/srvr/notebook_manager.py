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
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook = notebook_db[name]
        return repr(notebook)

    @staticmethod
    def ADD_NOTEBOOK(params, socket, address):
        """adds the notebook to the db"""
        name = params[NAME]
        notebook = ast.literal_eval(params[NOTE_BOOK])
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name] = notebook
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def ADD_STROKE(params, socket, address):
        """adds a stroke to the notebook from the db"""
        name = params[NAME]
        stroke = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[2]
        id = params[3]
        with NotebookManager.lock:
            if id == "0":
                id = NotebookManager._get_stroke_id_unlocked(name, id_page)
                stroke["id"] = id
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page]["strokes"][id] = stroke
            notebook_db[name]["last_change"] = str(float(params[4])+1.0)
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def DELETE_STROKE(params, socket, address):
        """deletes a stroke from the notebook in the db"""
        name = params[NAME]
        id_page = params[1]
        id = params[2]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page]["strokes"].pop(id)
            notebook_db[name]["last_change"] = params[3]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def CHANGE_BACKGROUND(params, socket, address):
        """change the background of the notebook from the db"""
        name = params[NAME]
        id_page = params[1]
        page_type = params[2]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page]["page_type"] = page_type
            notebook_db[name]["last_change"] = params[3]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def CLEAR(params, socket, address):
        """clears the strokes of the notebook from the db"""
        name = params[NAME]
        id = params[1]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id]["strokes"] = {}
            notebook_db[name]["last_change"] = params[2]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def ADD_PAGE(params, socket, address):
        """adds a page to the notebook in the db"""
        name = params[NAME]
        page = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[2]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page] = page
            notebook_db[name]["last_change"] = params[3]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def CHECK_UPDATES(params, socket, address):
        """checks if notebook has updates since the given timestamp"""
        name = params[NAME]
        time_stamp = params[1]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            last_change = float(notebook_db[name]["last_change"])
        if float(time_stamp) < last_change:
            return NotebookManager.GET_NOTEBOOK(params, socket, address)
        else:
            return "NO"


    @staticmethod
    def CHANGE_TIME_STAMP(name, time_stamp):
        """updates the timestamp for a notebook in the db"""
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["last_change"] = time_stamp
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def GET_STROKE_ID(params):
        """gets the next stroke id from the notebook from the db"""
        name = params[NAME]
        page_id = params[1]
        with NotebookManager.lock:
            return NotebookManager._get_stroke_id_unlocked(name, page_id)

    @staticmethod
    def _get_stroke_id_unlocked(name, page_id):
        """gets the next stroke id (must be called with lock held)"""
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        next_stroke_id = notebook_db[name]["pages"][page_id]["stroke_id"]
        temp = str(int(next_stroke_id) + 1)
        print(f"New Stroke is: ={next_stroke_id}= , Next stroke will be ={temp}=")
        notebook_db[name]["pages"][page_id]["stroke_id"] = temp
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        return next_stroke_id
