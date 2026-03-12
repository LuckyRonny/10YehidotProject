"""
Ronny Gets
Links users to notebooks and permissions; NotebookDB + NotebookManager.
"""
import sqlite3
from constants import (
    NAME_NOTEBOOK,
    NOTEBOOK,
    NOTEBOOK_ID,
    NOTEBOOK_NAME,
    USER_ID,
)
from notebook_manager import NotebookManager

# Index into params for permission; index into row for permission column
PERMISSION = 3
CHANGE_ACCESS_PARAMS_ACCESS_INDEX = 1
CHANGE_ACCESS_PARAMS_NOTEBOOK_NAME_INDEX = 2
NOTEBOOK_ID_ROW_INDEX = 0
USER_ID_ROW_INDEX = 0
PERMISSION_ROW_INDEX = 1
EXIST = 0
FIRST = 0
PERMISSIONS_ROW = 1


class UserNotebookManager(object):
    """Manages UsersNotebooks and Notebooks tables
     delegates content to NotebookManager."""

    @staticmethod
    def ADD_NOTEBOOK_TO_DB(params):
        """Add notebook to DB and to notebook manager
         return ok or error string."""
        user_id = params[USER_ID]
        notebook_name = params[NOTEBOOK_NAME]
        notebook = params[NOTEBOOK]
        per = int(params[PERMISSION])
        try:
            UserNotebookManager.add_to_db(notebook_name, user_id, per)
        except sqlite3.IntegrityError as e:
            return str(e)
        NotebookManager.ADD_NOTEBOOK([notebook_name, notebook])
        return "ok"

    @staticmethod
    def add_to_db(notebook_name, user_id, per):
        """Insert into Notebooks and UsersNotebooks; raises on duplicate."""
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Notebooks (name) VALUES (?)",
                (notebook_name,))
            conn.commit()
            notebook_id = cursor.lastrowid
            sql = ("INSERT INTO UsersNotebooks (user, notebook, permission) "
                   "VALUES (?, ?, ?)")
            cursor.execute(sql, (user_id, notebook_id, per))
            conn.commit()

    @staticmethod
    def CLIENTS_NOTEBOOKS(params):
        """gets all the notebooks of the user"""
        user_id = params[USER_ID]
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT notebook, permission FROM UsersNotebooks "
                "WHERE user = ? AND permission != 3",
                (user_id,))
            notebooks_id_tuple = cursor.fetchall()
            notebooks_id = [row[NOTEBOOK_ID] for row in notebooks_id_tuple]
            permissions = [row[PERMISSIONS_ROW] for row in notebooks_id_tuple]
            notebooks_names = []
            for i in range(len(notebooks_id)):
                name = UserNotebookManager.get_all_notebooks(notebooks_id[i],
                                                             cursor,
                                                             notebooks_names)
                notebooks_names.append(name + "," + str(permissions[i]))
        names = "!".join(notebooks_names)
        return names

    @staticmethod
    def get_all_notebooks(id, cursor, notebooks_names):
        """Resolve notebook id to name via Notebooks table
         return name string."""
        cursor.execute(
            "SELECT name FROM Notebooks WHERE id = ?",
            (id,))
        name = cursor.fetchone()[NAME_NOTEBOOK]
        return str(name)

    @staticmethod
    def _resolve_user_id(cursor, user_name):
        """Return user id for user_name from Users table."""
        cursor.execute("SELECT id FROM Users WHERE user_name = ?",
                       (user_name,))
        row = cursor.fetchone()
        return row[USER_ID_ROW_INDEX] if row else None

    @staticmethod
    def _resolve_notebook_id(cursor, notebook_name):
        """Return notebook id for notebook_name from Notebooks table."""
        cursor.execute("SELECT id FROM Notebooks WHERE name = ?",
                       (notebook_name,))
        row = cursor.fetchone()
        return row[NOTEBOOK_ID_ROW_INDEX] if row else None

    @staticmethod
    def _user_notebook_exists(cursor, user_id, notebook_id):
        """Return True if (user_id, notebook_id) exists in UsersNotebooks."""
        cursor.execute(
            "SELECT COUNT(*) FROM UsersNotebooks WHERE user=? AND notebook=?",
            (user_id, notebook_id))
        return cursor.fetchone()[FIRST] > EXIST

    @staticmethod
    def CHANGE_ACCESS(params):
        """Set or update permission for user on notebook; insert if no row."""
        user_name = params[USER_ID]
        access = params[CHANGE_ACCESS_PARAMS_ACCESS_INDEX]
        notebook_name = params[CHANGE_ACCESS_PARAMS_NOTEBOOK_NAME_INDEX]
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            user_id = UserNotebookManager._resolve_user_id(cursor, user_name)
            notebook_id = UserNotebookManager._resolve_notebook_id(
                cursor, notebook_name)
            if user_id is None or notebook_id is None:
                return "ok"
            exists = UserNotebookManager._user_notebook_exists(
                cursor, user_id, notebook_id)
            if exists:
                cursor.execute(
                    "UPDATE UsersNotebooks SET permission=? "
                    "WHERE user=? AND notebook=?",
                    (access, user_id, notebook_id))
            else:
                cursor.execute(
                    "INSERT INTO UsersNotebooks "
                    "(user, notebook, permission) VALUES (?, ?, ?)",
                    (user_id, notebook_id, access))
            conn.commit()
        return "ok"
