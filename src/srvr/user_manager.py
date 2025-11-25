"""
Ronny Gets
user manager server
"""

import threading
import sqlite3
from constants import *


class UserManager(object):

    @staticmethod
    def LOGIN(params, socket, address):
        """
        check if has a user with this username and password
        """
        username = params[USER_NAME]
        password = params[PASSWORD]
        conn = sqlite3.connect('NotebookDB.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Users WHERE user_name = ? AND password = ?",
            (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            return str(user[ID_OF_USER]) + "!" + str(user[1])
        else:

            return "False"


    @staticmethod
    def SIGNUP(params, socket, address):
        """
        creates a new user
        """
        username = params[USER_NAME]
        password = params[PASSWORD]
        name = params[SIGNUP_NAME]
        conn = sqlite3.connect('NotebookDB.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Users (user_name, password, name) VALUES (?, ?, ?)",
                (username, password, name))
            conn.commit()
            id = cursor.lastrowid
            conn.close()
            if id:
                return str(id)
            else:
                return "False"
        except sqlite3.IntegrityError:
            return "False"
