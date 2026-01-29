"""
Ronny Gets
notebook user manager server
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

PERMISSION = 3


class UserNotebookManager(object):
    @staticmethod
    def ADD_NOTEBOOK_TO_DB(params):
        """add the notebook to both dbs """
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
        """adds the notebook to db"""
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
                "SELECT notebook, permission FROM UsersNotebooks WHERE user = ?",
                (user_id,))
            notebooks_id_tuple = cursor.fetchall()
            notebooks_id = [row[NOTEBOOK_ID] for row in notebooks_id_tuple]
            notebooks_names = []
            for id in notebooks_id:
                name = UserNotebookManager.get_all_notebooks(id, cursor,
                                                             notebooks_names)
                notebooks_names.append(name + ",")
        names = "!".join(notebooks_names)
        return names

    @staticmethod
    def get_all_notebooks(id, cursor, notebooks_names):
        """gets all the notebooks names"""
        cursor.execute(
            "SELECT name FROM Notebooks WHERE id = ?",
            (id,))
        name = cursor.fetchone()[NAME_NOTEBOOK]
        return str(name)

    @staticmethod
    def CHANGE_ACCESS(params):
        """gchange the access"""
        user_name = params[USER_ID]
        access = params[1]
        notebook_name = params[2]
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM Users WHERE user_name = ?",
                (user_name,))
            user_id_tuple = cursor.fetchone()
            user_id = user_id_tuple[0]
            cursor.execute(
                "SELECT id FROM Notebooks WHERE name = ?",
                (notebook_name,))
            notebook_id_tuple = cursor.fetchone()
            notebook_id = notebook_id_tuple[0]
            cursor.execute(
                "INSERT INTO UsersNotebooks (user, notebook, permission) VALUES (?)",
                (notebook_name, notebook_id, access)
            )
        return "ok"
