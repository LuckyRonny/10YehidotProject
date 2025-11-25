"""
Ronny Gets
notebook user manager server
"""
import sqlite3

from notebook_manager import *


class UserNotebookManager(object):

    @staticmethod
    def ADD_NOTEBOOK_TO_DB(params, socket, address):
        """
        """
        user_id = params[0]
        notebook_name = params[1]
        notebook = params[2]
        conn = sqlite3.connect('NotebookDB.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Notebooks (name) VALUES (?)",
                (notebook_name,))
            conn.commit()
            notebook_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO UsersNotebooks (user, notebook) VALUES (?, ?)",
                (user_id, notebook_id))
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError as e:
            return str(e)
        NotebookManager.ADD_NOTEBOOK([notebook_name, notebook], None, None)
        return "ok"

    @staticmethod
    def CLIENTS_NOTEBOOKS(params, socket, address):
        """

        """
        user_id = params[0]
        conn = sqlite3.connect('NotebookDB.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT notebook FROM UsersNotebooks WHERE user = ?",
            (user_id,))
        notebooks_id_tuple = cursor.fetchall()
        notebooks_id = [row[0] for row in notebooks_id_tuple]
        notebooks_names = []
        for id in notebooks_id:
            cursor.execute(
                "SELECT name FROM Notebooks WHERE id = ?",
                (id,))
            name = cursor.fetchone()[0]
            notebooks_names.append(str(name))
        conn.close()
        names = "!".join(notebooks_names)
        return names

