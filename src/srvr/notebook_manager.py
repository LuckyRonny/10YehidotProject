"""
Ronny Getz
Notebook manager server
Handles notebooks pages strokes and updates
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
UPDATES_MAX_LEN = 10
UPDATES_TRIM_TO = 5
INDENT = 2

BASE_DIR = "server_data"
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")
UPDATES_DIR = os.path.join(BASE_DIR, "updates")

os.makedirs(NOTEBOOKS_DIR, exist_ok=True)
os.makedirs(UPDATES_DIR, exist_ok=True)


class NotebookManager(object):
    lock = threading.Lock()

    @staticmethod
    def _notebook_path(name):
        """
        Return the path to the notebook JSON file
        """
        return os.path.join(NOTEBOOKS_DIR, f"{name}.json")

    @staticmethod
    def _updates_path(name):
        """
        Return the path to the updates JSON file for the notebook
        """
        return os.path.join(UPDATES_DIR, f"updates_{name}.json")

    @staticmethod
    def _atomic_write(path, data):
        """
        Write JSON to file using a temporary file
        Replace file atomically to prevent corruption
        """
        dir_name = os.path.dirname(path)
        with tempfile.NamedTemporaryFile(
            "w", dir=dir_name, delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(data, tmp, indent=INDENT)
            tmp_name = tmp.name
        os.replace(tmp_name, path)

    @staticmethod
    def _load(path, default=None):
        """
        Load JSON from file
        Return default if file does not exist
        """
        if not os.path.exists(path):
            return default if default is not None else {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _parse_param(param):
        """
        Convert parameter to dict if it is a string
        Return dict unchanged if already dict
        """
        if isinstance(param, str):
            return ast.literal_eval(param)
        return param

    @staticmethod
    def GET_NOTEBOOK(params):
        """
        Return notebook content as string representation
        """
        name = params[NAME]
        with NotebookManager.lock:
            notebook = NotebookManager._load(
                NotebookManager._notebook_path(name), {}
            )
        return repr(notebook)

    @staticmethod
    def ADD_NOTEBOOK(params):
        """
        Add or overwrite notebook
        Create updates file if it does not exist
        """
        name = params[NAME]
        notebook = NotebookManager._parse_param(params[NOTE_BOOK])
        with NotebookManager.lock:
            NotebookManager._atomic_write(
                NotebookManager._notebook_path(name), notebook
            )
            if not os.path.exists(NotebookManager._updates_path(name)):
                NotebookManager._atomic_write(
                    NotebookManager._updates_path(name), []
                )
        return "ok"

    @staticmethod
    def ADD_STROKE(params):
        """
        Add stroke to a page
        Assign stroke id if zero
        Update last_change timestamp
        """
        name = params[NAME]
        stroke = NotebookManager._parse_param(params[NOTE_BOOK])
        id_page = params[ID_PAGE]
        sid = params[ID_STROKE]
        ts = time.time()

        with NotebookManager.lock:
            notebook = NotebookManager._load(
                NotebookManager._notebook_path(name), {}
            )
            if "pages" not in notebook:
                notebook["pages"] = {}
            if id_page not in notebook["pages"]:
                notebook["pages"][id_page] = {"strokes": {}, "stroke_id": "1"}

            page = notebook["pages"][id_page]
            if sid == "0":
                sid = page.get("stroke_id", "1")
                page["stroke_id"] = str(int(sid) + NEXT_STROKE)
                stroke["id"] = sid

            page["strokes"][sid] = stroke
            notebook["last_change"] = max(
                float(notebook.get("last_change", 0)), float(ts)
            )
            NotebookManager._atomic_write(
                NotebookManager._notebook_path(name), notebook
            )

        NotebookManager.create_update(name, ts, "ADD_STROKE", id_page, stroke)
        return sid

    @staticmethod
    def DELETE_STROKE(params):
        """
        Delete stroke from page
        Update last_change timestamp
        """
        name = params[NAME]
        id_page = params[PAGE_ID]
        sid = params[STROKE_ID]
        ts = time.time()

        with NotebookManager.lock:
            notebook = NotebookManager._load(
                NotebookManager._notebook_path(name), {}
            )
            if "pages" not in notebook or id_page not in notebook["pages"]:
                return "page_not_found"
            page = notebook["pages"][id_page]
            if sid not in page["strokes"]:
                return "stroke_not_found"

            del page["strokes"][sid]
            notebook["last_change"] = max(
                float(notebook.get("last_change", 0)), float(ts)
            )
            NotebookManager._atomic_write(
                NotebookManager._notebook_path(name), notebook
            )

        NotebookManager.create_update(name, ts, "DELETE_STROKE", id_page, sid)
        return "ok"

    @staticmethod
    def ADD_PAGE(params):
        """
        Add a page to a notebook
        Create strokes dict and stroke_id if missing
        """
        name = params[NAME]
        page_data = NotebookManager._parse_param(params[NOTE_BOOK])
        id_page = params[ID_PAGE]
        ts = time.time()

        with NotebookManager.lock:
            notebook = NotebookManager._load(
                NotebookManager._notebook_path(name), {}
            )
            if "pages" not in notebook:
                notebook["pages"] = {}
            notebook["pages"][id_page] = page_data
            notebook["pages"][id_page].setdefault("stroke_id", "1")
            notebook["pages"][id_page].setdefault("strokes", {})

            notebook["last_change"] = max(
                float(notebook.get("last_change", 0)), float(ts)
            )
            NotebookManager._atomic_write(
                NotebookManager._notebook_path(name), notebook
            )

        NotebookManager.create_update(name, ts, "ADD_PAGE", id_page, page_data)
        return "ok"

    @staticmethod
    def CLEAR(params):
        """
        Clear all strokes from a page
        Update last_change timestamp
        """
        name = params[NAME]
        id_page = params[PAGE_ID]
        ts = time.time()
        with NotebookManager.lock:
            notebook = NotebookManager._load(
                NotebookManager._notebook_path(name), {})
            if "pages" not in notebook or id_page not in notebook["pages"]:
                return "page_not_found"

            notebook["pages"][id_page]["strokes"] = {}
            notebook["last_change"] = max(
                float(notebook.get("last_change", 0)), float(ts)
            )
            NotebookManager._atomic_write(
                NotebookManager._notebook_path(name), notebook
            )

        NotebookManager.create_update(name, ts, "CLEAR", id_page, None)
        return "ok"

    @staticmethod
    def CHANGE_BACKGROUND(params):
        """
        Change background type of page
        Update last_change timestamp
        """
        name = params[NAME]
        id_page = params[PAGE_ID]
        page_type = params[PAGE_TYPE]
        ts = time.time()
        with NotebookManager.lock:
            notebook = NotebookManager._load(
                NotebookManager._notebook_path(name), {}
            )
            if "pages" not in notebook or id_page not in notebook["pages"]:
                return "page_not_found"

            notebook["pages"][id_page]["page_type"] = page_type
            notebook["last_change"] = max(
                float(notebook.get("last_change", 0)), float(ts)
            )
            NotebookManager._atomic_write(
                NotebookManager._notebook_path(name), notebook
            )

        NotebookManager.create_update(
            name, ts, "CHANGE_BACKGROUND", id_page, page_type
        )
        return "ok"

    @staticmethod
    def CHECK_UPDATES(params):
        """
        Return list of updates newer than timestamp
        """
        name = params[NAME]
        time_stamp = params[TIME_STAMP]
        with NotebookManager.lock:
            updates_data = NotebookManager._load(
                NotebookManager._updates_path(name), []
            )

        if isinstance(updates_data, dict):
            updates_list = updates_data.get(name, [])
        elif isinstance(updates_data, list):
            updates_list = updates_data
        else:
            updates_list = []

        updates = [
            u for u in updates_list if float(u["ts"]) > float(time_stamp)
        ]
        return repr(updates)

    @staticmethod
    def create_update(notebook_name, ts, type, id_page, data):
        """
        Append update to notebook JSON
        Trim updates if over max length
        """
        update = {"ts": ts, "type": type, "page": id_page, "data": data}
        with NotebookManager.lock:
            updates_data = NotebookManager._load(
                NotebookManager._updates_path(notebook_name), []
            )
            if isinstance(updates_data, dict):
                updates_list = updates_data.get(notebook_name, [])
            elif isinstance(updates_data, list):
                updates_list = updates_data
            else:
                updates_list = []

            updates_list.append(update)
            if len(updates_list) >= UPDATES_MAX_LEN:
                updates_list = updates_list[-UPDATES_TRIM_TO:]

            NotebookManager._atomic_write(
                NotebookManager._updates_path(notebook_name), updates_list
            )
