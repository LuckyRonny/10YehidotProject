"""
Ronny Getz
methods
"""

import user_manager
import notebook_manager
import user_notebook_manager


class Methods(object):
    @staticmethod
    def USERS(request, params):
        """move to user manager"""
        cls = getattr(user_manager, "UserManager")
        return getattr(cls, request)(params)

    @staticmethod
    def NOTEBOOKS(request, params):
        """move to notebook manager"""
        cls = getattr(notebook_manager, "NotebookManager")
        return getattr(cls, request)(params)

    @staticmethod
    def USERS_NOTEBOOKS(request, params):
        """move to user notebook manager"""
        cls = getattr(user_notebook_manager, "UserNotebookManager")
        return getattr(cls, request)(params)
