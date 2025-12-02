"""
Ronny Getz
methods
"""

import user_manager
import notebook_manager
import user_notebook_manager


class Methods(object):
    @staticmethod
    def USERS(request, params, socket, address):
        """move to user manager"""
        cls = getattr(user_manager, "UserManager")
        return getattr(cls, request)(params, socket, address)

    @staticmethod
    def NOTEBOOKS(request, params, socket, address):
        """move to notebook manager"""
        cls = getattr(notebook_manager, "NotebookManager")
        return getattr(cls, request)(params, socket, address)

    @staticmethod
    def USERS_NOTEBOOKS(request, params, socket, address):
        """move to user notebook manager"""
        cls = getattr(user_notebook_manager, "UserNotebookManager")
        return getattr(cls, request)(params, socket, address)
