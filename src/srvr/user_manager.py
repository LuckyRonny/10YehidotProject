"""
Ronny Gets
User manager: login, signup, all_users via SQLite.
"""
import sqlite3
from my_sha256 import Hasha256
from constants import ID_OF_USER, PASSWORD, SIGNUP_NAME, USER_NAME
from user_notebook_manager import *

# Index of display name in user row; default permission when not in notebook
NAME_OF_USER = 1
LOGIN_FAIL_RESPONSE = "False"
DEFAULT_PERMISSION = 3
ALL_USERS_PARAMS_NOTEBOOK_INDEX = 1
PERMISSION = 1
ID = 1


class UserManager(object):
    @staticmethod
    def LOGIN(params):
        """Validate username/password
         return id!name or LOGIN_FAIL_RESPONSE."""
        username = params[USER_NAME]
        password = params[PASSWORD]
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Users WHERE user_name = ? AND password = ?",
                (username, Hasha256.get_hash_hex(password)))
            user = cursor.fetchone()
        if user:
            return str(user[ID_OF_USER]) + "!" + str(user[NAME_OF_USER])
        return LOGIN_FAIL_RESPONSE

    @staticmethod
    def SIGNUP(params):
        """Insert new user; return id string or
        LOGIN_FAIL_RESPONSE on duplicate."""
        username = params[USER_NAME]
        password = params[PASSWORD]
        name = params[SIGNUP_NAME]
        try:
            with sqlite3.connect('NotebookDB.db') as conn:
                cursor = conn.cursor()
                sql = ("INSERT INTO Users (user_name, password, name)" +
                       "VALUES (?, ?, ?)")
                cursor.execute(sql, (username,
                                     Hasha256.get_hash_hex(password), name))
                conn.commit()
                id = cursor.lastrowid
            if id:
                return str(id)
            return LOGIN_FAIL_RESPONSE
        except sqlite3.IntegrityError:
            return LOGIN_FAIL_RESPONSE

    @staticmethod
    def ALL_USERS(params):
        """Return user list with permissions for notebook"""
        excluded_user = params[USER_NAME]
        notebook = params[ALL_USERS_PARAMS_NOTEBOOK_INDEX]
        usernames_ids, ids_permissions = UserManager.get_id_permission(
            excluded_user, notebook)
        perms_by_id = {row[USER_NAME]: row[PERMISSION]
                       for row in ids_permissions}
        usernames = [row[USER_NAME] for row in usernames_ids]
        ids = [row[ID] for row in usernames_ids]
        parts = []
        for i in range(len(ids)):
            perm = perms_by_id.get(ids[i], DEFAULT_PERMISSION)
            parts.append(usernames[i] + "," + str(perm))
        return "!".join(parts)

    @staticmethod
    def get_id_permission(excluded_user, notebook):
        """Fetch (user_name, id) and (user, permission) for notebook
         exclude one user."""
        with sqlite3.connect('NotebookDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_name, id FROM users WHERE id != ?",
                (excluded_user,)
            )
            usernames_ids = cursor.fetchall()
            notebook = UserNotebookManager._resolve_notebook_id(cursor,
                                                                notebook)
            cursor.execute(
                "SELECT user, permission FROM UsersNotebooks "
                "WHERE notebook == ?",
                (notebook,)
            )
            ids_permissions = cursor.fetchall()
        return usernames_ids, ids_permissions
