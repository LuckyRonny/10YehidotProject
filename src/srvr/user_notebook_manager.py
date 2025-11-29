"""
Ronny Gets
notebook user manager server
"""

import sqlite3
from notebook_manager import *


class UserNotebookManager(object):
    @staticmethod
    def ADD_NOTEBOOK_TO_DB(params, socket, address):
        """add the notebook to both dbs """
        user_id = params[USER_ID]
        notebook_name = params[NOTEBOOK_NAME]
        notebook = params[NOTEBOOK]
        try:
            UserNotebookManager.add_to_db(notebook_name, user_id)
        except sqlite3.IntegrityError as e:
            return str(e)
        NotebookManager.ADD_NOTEBOOK([notebook_name, notebook],
                                     None, None)
        return "ok"

    @staticmethod
    def add_to_db(notebook_name, user_id):
        """adds the notebook to db"""
        conn = sqlite3.connect('NotebookDB.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Notebooks (name) VALUES (?)",
            (notebook_name,))
        conn.commit()
        notebook_id = cursor.lastrowid
        sql = "INSERT INTO UsersNotebooks (user, notebook) VALUES (?, ?)"
        cursor.execute(sql, (user_id, notebook_id))
        conn.commit()
        conn.close()

    @staticmethod
    def CLIENTS_NOTEBOOKS(params, socket, address):
        """gets all the notebooks of the user"""
        user_id = params[USER_ID]
        conn = sqlite3.connect('NotebookDB.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT notebook FROM UsersNotebooks WHERE user = ?",
            (user_id,))
        notebooks_id_tuple = cursor.fetchall()
        notebooks_id = [row[NOTEBOOK_ID] for row in notebooks_id_tuple]
        notebooks_names = []
        for id in notebooks_id:
            UserNotebookManager.get_all_notebooks(id, cursor, notebooks_names)
        conn.close()
        names = "!".join(notebooks_names)
        return names

    @staticmethod
    def get_all_notebooks(id, cursor, notebooks_names):
        """gets all the notebooks names"""
        cursor.execute(
            "SELECT name FROM Notebooks WHERE id = ?",
            (id,))
        name = cursor.fetchone()[NAME_NOTEBOOK]
        notebooks_names.append(str(name))
