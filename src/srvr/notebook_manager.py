"""
Ronny Getz
Notebook manager server
"""

import ast
import json
import threading

from constants import *
ID_PAGE = 2
ID_STROKE = 3
TIME_STAMP_STROKE = 4
TIME_STAMP = 3
PAGE_ID = 1
STROKE_ID = 2
PAGE_TYPE = 2
NEXT_STROKE = 1
LOADING_TIME = 1.0
TIME_STAMP_CLEAR = 2
TIME_STAMP_CHECK = 1


class NotebookManager(object):
    lock = threading.Lock()

    @staticmethod
    def GET_NOTEBOOK(params):
        """gets the notebook from the db"""
        name = params[NAME]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook = notebook_db[name]
        return repr(notebook)

    @staticmethod
    def ADD_NOTEBOOK(params):
        """adds the notebook to the db"""
        name = params[NAME]
        notebook = ast.literal_eval(params[NOTE_BOOK])
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name] = notebook
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
            with open("updates.json", "r") as f:
                updates = json.load(f)
            updates[name] = []
            with open("updates.json", "w") as f:
                json.dump(updates, f)
        return "ok"

    @staticmethod
    def ADD_STROKE(params):
        """adds a stroke to the notebook from the db"""
        name = params[NAME]
        stroke = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[ID_PAGE]
        id = params[ID_STROKE]
        with NotebookManager.lock:
            if id == "0":
                id = NotebookManager._get_stroke_id_unlocked(name, id_page)
                stroke["id"] = id
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page]["strokes"][id] = stroke
            notebook_db[name]["last_change"] = params[TIME_STAMP_STROKE]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        NotebookManager.create_update(name, params[TIME_STAMP_STROKE],
                                      "ADD_STROKE", id_page, stroke)
        return id

    @staticmethod
    def DELETE_STROKE(params):
        """deletes a stroke from the notebook in the db"""
        name = params[NAME]
        id_page = params[PAGE_ID]
        id = params[STROKE_ID]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page]["strokes"].pop(id)
            notebook_db[name]["last_change"] = params[TIME_STAMP]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def CHANGE_BACKGROUND(params):
        """change the background of the notebook from the db"""
        name = params[NAME]
        id_page = params[PAGE_ID]
        page_type = params[PAGE_TYPE]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page]["page_type"] = page_type
            notebook_db[name]["last_change"] = params[TIME_STAMP]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def CLEAR(params):
        """clears the strokes of the notebook from the db"""
        name = params[NAME]
        id = params[PAGE_ID]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id]["strokes"] = {}
            notebook_db[name]["last_change"] = params[TIME_STAMP_CLEAR]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def ADD_PAGE(params):
        """adds a page to the notebook in the db"""
        name = params[NAME]
        page = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[ID_PAGE]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page] = page
            notebook_db[name]["last_change"] = params[TIME_STAMP]
            with open("notebook_DB.json", "w") as f:
                json.dump(notebook_db, f)
        return "ok"

    @staticmethod
    def CHECK_UPDATES(params):
        """checks if notebook has updates since the given timestamp"""
        name = params[NAME]
        time_stamp = params[TIME_STAMP_CHECK]
        with NotebookManager.lock:
            with open("updates.json", "r") as f:
                updates_db = json.load(f)
        updates = []
        for u in updates_db[name]:
            if float(u["ts"]) > float(time_stamp):
                updates.append(u)
        return repr(updates)

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
        page_id = params[PAGE_ID]
        with NotebookManager.lock:
            return NotebookManager._get_stroke_id_unlocked(name, page_id)

    @staticmethod
    def _get_stroke_id_unlocked(name, page_id):
        """gets the next stroke id (must be called with lock held)"""
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)
        next_stroke_id = notebook_db[name]["pages"][page_id]["stroke_id"]
        temp = str(int(next_stroke_id) + NEXT_STROKE)
        print(f"New Stroke is: ={next_stroke_id}= , "
              f"Next stroke will be ={temp}=")
        notebook_db[name]["pages"][page_id]["stroke_id"] = temp
        with open("notebook_DB.json", "w") as f:
            json.dump(notebook_db, f)
        return next_stroke_id

    @staticmethod
    def create_update(notebook_name, time, type, page_id, data):
        """create the update and at it to a list of updates"""
        update = {
            "ts": time,
            "type": type,
            "page": page_id,
            "data": data
        }
        with NotebookManager.lock:
            with open("updates.json", "r") as f:
                updates = json.load(f)
            updates[notebook_name].append(update)
            with open("updates.json", "w") as f:
                json.dump(updates, f)
