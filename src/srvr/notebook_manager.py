"""
Ronny Getz
Notebook manager server
"""

import ast
import json
import threading
import os
import tempfile

from constants import NAME, NOTE_BOOK

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
    def _atomic_write(path, data):
        dir_name = os.path.dirname(path) or "."
        with tempfile.NamedTemporaryFile("w", dir=dir_name,
                                         delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_name = tmp.name
        os.replace(tmp_name, path)

    @staticmethod
    def GET_NOTEBOOK(params):
        name = params[NAME]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook = notebook_db[name]
        return repr(notebook)

    @staticmethod
    def ADD_NOTEBOOK(params):
        name = params[NAME]
        notebook = ast.literal_eval(params[NOTE_BOOK])

        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name] = notebook
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

            # FIX: do NOT override existing updates
            with open("updates.json", "r") as f:
                updates = json.load(f)

            updates.setdefault(name, [])
            NotebookManager._atomic_write("updates.json", updates)

        return "ok"

    @staticmethod
    def ADD_STROKE(params):
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
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)
            NotebookManager.create_update_unlocked(
                name, params[TIME_STAMP_STROKE], "ADD_STROKE",
                id_page, stroke)
        return id

    @staticmethod
    def DELETE_STROKE(params):
        name = params[NAME]
        id_page = params[PAGE_ID]
        id = params[STROKE_ID]

        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id_page]["strokes"].pop(id)
            notebook_db[name]["last_change"] = params[TIME_STAMP]
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

            NotebookManager.create_update_unlocked(
                name, params[TIME_STAMP], "DELETE_STROKE", id_page, id
            )
        return "ok"

    @staticmethod
    def CHANGE_BACKGROUND(params):
        name = params[NAME]
        id_page = params[PAGE_ID]
        page_type = params[PAGE_TYPE]

        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id_page]["page_type"] = page_type
            notebook_db[name]["last_change"] = params[TIME_STAMP]
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

            NotebookManager.create_update_unlocked(
                name, params[TIME_STAMP], "CHANGE_BACKGROUND",
                id_page, page_type)
        return "ok"

    @staticmethod
    def CLEAR(params):
        name = params[NAME]
        id = params[PAGE_ID]

        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id]["strokes"] = {}
            notebook_db[name]["last_change"] = params[TIME_STAMP_CLEAR]
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

            NotebookManager.create_update_unlocked(
                name, params[TIME_STAMP_CLEAR], "CLEAR", id, None
            )
        return "ok"

    @staticmethod
    def ADD_PAGE(params):
        name = params[NAME]
        page = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[ID_PAGE]
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page] = page
            notebook_db[name]["last_change"] = params[TIME_STAMP]
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

            NotebookManager.create_update_unlocked(
                name, params[TIME_STAMP], "ADD_PAGE", id_page, page
            )
        return "ok"

    @staticmethod
    def CHECK_UPDATES(params):
        name = params[NAME]
        time_stamp = params[TIME_STAMP_CHECK]

        with NotebookManager.lock:
            with open("updates.json", "r") as f:
                updates_db = json.load(f)

        updates = []
        client_ts = float(time_stamp)
        for u in updates_db.get(name, []):
            update_ts = float(u["ts"])
            if update_ts > client_ts or abs(update_ts - client_ts) < 0.1:
                updates.append(u)

        return repr(updates)

    @staticmethod
    def _get_stroke_id_unlocked(name, page_id):
        """gets the stroke id"""
        with open("notebook_DB.json", "r") as f:
            notebook_db = json.load(f)

        next_stroke_id = notebook_db[name]["pages"][page_id]["stroke_id"]
        notebook_db[name]["pages"][page_id]["stroke_id"] = str(
            int(next_stroke_id) + NEXT_STROKE
        )

        NotebookManager._atomic_write("notebook_DB.json", notebook_db)
        return str(next_stroke_id)

    @staticmethod
    def create_update(notebook_name, time, type, page_id, data):
        """Create an update"""
        update = {
            "ts": time,
            "type": type,
            "page": page_id,
            "data": data
        }

        with NotebookManager.lock:
            with open("updates.json", "r") as f:
                updates = json.load(f)

            updates.setdefault(notebook_name, [])
            updates[notebook_name].append(update)

            NotebookManager._atomic_write("updates.json", updates)

    @staticmethod
    def create_update_unlocked(notebook_name, time, type, page_id, data):
        """Create an update"""
        update = {
            "ts": time,
            "type": type,
            "page": page_id,
            "data": data
        }

        with open("updates.json", "r") as f:
            updates = json.load(f)

        updates.setdefault(notebook_name, [])
        updates[notebook_name].append(update)
        NotebookManager._atomic_write("updates.json", updates)
