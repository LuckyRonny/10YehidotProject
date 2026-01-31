"""
Ronny Getz
Notebook manager server
"""

import ast
import json
import threading
import os
import tempfile
import time

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

    # ---------- FIX: atomic json write ----------
    @staticmethod
    def _atomic_write(path, data):
        dir_name = os.path.dirname(path) or "."
        with tempfile.NamedTemporaryFile("w", dir=dir_name,
                                         delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            tmp_name = tmp.name
        os.replace(tmp_name, path)

    # -------------------------------------------

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
        sid = params[ID_STROKE]
        ts = time.time()
        with NotebookManager.lock:
            if sid == "0":
                sid = NotebookManager._get_stroke_id_unlocked(name, id_page)
                stroke["id"] = sid

            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id_page]["strokes"][sid] = stroke
            notebook_db[name]["last_change"] = max(
                float(notebook_db[name]["last_change"]),
                float(ts)
            )
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

        NotebookManager.create_update(
            name, ts, "ADD_STROKE", id_page, stroke
        )
        return sid

    @staticmethod
    def DELETE_STROKE(params):
        name = params[NAME]
        id_page = params[PAGE_ID]
        id = params[STROKE_ID]
        ts = time.time()
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id_page]["strokes"].pop(id)
            notebook_db[name]["last_change"] = max(
                float(notebook_db[name]["last_change"]),
                float(ts)
            )
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

        NotebookManager.create_update(
            name, ts, "DELETE_STROKE", id_page, id
        )
        return "ok"

    @staticmethod
    def CHANGE_BACKGROUND(params):
        name = params[NAME]
        id_page = params[PAGE_ID]
        page_type = params[PAGE_TYPE]
        ts = time.time()
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id_page]["page_type"] = page_type
            notebook_db[name]["last_change"] = max(
                float(notebook_db[name]["last_change"]),
                float(ts)
            )
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

        NotebookManager.create_update(
            name, ts, "CHANGE_BACKGROUND", id_page, page_type
        )
        return "ok"

    @staticmethod
    def CLEAR(params):
        name = params[NAME]
        id = params[PAGE_ID]
        ts = time.time()
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)

            notebook_db[name]["pages"][id]["strokes"] = {}
            notebook_db[name]["last_change"] = max(
                float(notebook_db[name]["last_change"]),
                float(ts)
            )
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)

        NotebookManager.create_update(
            name, ts, "CLEAR", id, None
        )
        return "ok"

    @staticmethod
    def ADD_PAGE(params):
        name = params[NAME]
        page = ast.literal_eval(params[NOTE_BOOK])
        id_page = params[ID_PAGE]
        ts = time.time()
        with NotebookManager.lock:
            with open("notebook_DB.json", "r") as f:
                notebook_db = json.load(f)
            notebook_db[name]["pages"][id_page] = page
            notebook_db[name]["last_change"] = max(
                float(notebook_db[name]["last_change"]),
                float(ts)
            )
            NotebookManager._atomic_write("notebook_DB.json", notebook_db)
        NotebookManager.create_update(
            name, ts, "ADD_PAGE", id_page, page
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
        for u in updates_db.get(name, []):
            if float(u["ts"]) > float(time_stamp):
                updates.append(u)

        return repr(updates)

    @staticmethod
    def _get_stroke_id_unlocked(name, page_id):
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
            notebook_u = updates[notebook_name]
            notebook_u.append(update)
            if len(notebook_u) >= 15:
                notebook_u = notebook_u[-10:]
            updates[notebook_name] = notebook_u
            NotebookManager._atomic_write("updates.json", updates)
