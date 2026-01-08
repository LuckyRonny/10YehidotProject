"""
Ronny Gets
user manager server
"""

import sqlite3

from constants import ID_OF_USER, PASSWORD, SIGNUP_NAME, USER_NAME

NAME_OF_USER = 1


class UserManager(object):

    @staticmethod
    def LOGIN(params):
        """
        check if has a user with this username and password
        """
        username = params[USER_NAME]
        password = params[PASSWORD]
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Users WHERE user_name = ? AND password = ?",
                (username, password))
            user = cursor.fetchone()
        if user:
            return str(user[ID_OF_USER]) + "!" + str(user[NAME_OF_USER])
        else:
            return "False"

    @staticmethod
    def SIGNUP(params):
        """
        creates a new user
        """
        username = params[USER_NAME]
        password = params[PASSWORD]
        name = params[SIGNUP_NAME]
        try:
            with sqlite3.connect('NotebookDB.db') as conn:
                cursor = conn.cursor()
                sql = ("INSERT INTO Users (user_name, password, name)" +
                       "VALUES (?, ?, ?)")
                cursor.execute(sql, (username, password, name))
                conn.commit()
                id = cursor.lastrowid
            if id:
                return str(id)
            else:
                return "False"
        except sqlite3.IntegrityError:
            return "False"
