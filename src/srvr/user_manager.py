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

    @staticmethod
    def ALL_USERS(params):
        """gets all users except the user"""
        excluded_user = params[USER_NAME]
        notebook = params[1]
        usernames_ids, ids_permissions = UserManager.get_id_permission(
            excluded_user, notebook)
        dict = {}
        for row in ids_permissions:
            dict[row[0]] = row[1]
        usernames = [row[0] for row in usernames_ids]
        ids = [row[1] for row in usernames_ids]
        users_str = ""
        for i in range(len(ids)):
            if ids[i] in dict.keys():
                users_str += usernames[i] + "," + str(dict[ids[i]])
            else:
                users_str += usernames[i] + ",3"
            users_str += "!"
        return users_str[:-1]

    @staticmethod
    def get_id_permission(excluded_user, notebook):
        """"""
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_name, id FROM users WHERE id != ?",
                (excluded_user,)
            )
            usernames_ids = cursor.fetchall()
            cursor.execute(
                "SELECT user, permission FROM UsersNotebooks WHERE notebook != ?",
                (notebook,)
            )
            ids_permissions = cursor.fetchall()
        return usernames_ids, ids_permissions
