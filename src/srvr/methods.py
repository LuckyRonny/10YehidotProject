"""
Ronny Getz
Server request routing: delegates USERS, NOTEBOOKS, USERS_NOTEBOOKS to managers.
"""
import user_manager
import notebook_manager
import user_notebook_manager

USER_MANAGER_CLASS_NAME = "UserManager"
NOTEBOOK_MANAGER_CLASS_NAME = "NotebookManager"
USER_NOTEBOOK_MANAGER_CLASS_NAME = "UserNotebookManager"


class Methods(object):
    """Dispatches requests to UserManager, NotebookManager, or UserNotebookManager."""

    @staticmethod
    def USERS(request, params):
        """Delegate to user manager; handles login, signup, all_users, etc."""
        cls = getattr(user_manager, USER_MANAGER_CLASS_NAME)
        return getattr(cls, request)(params)

    @staticmethod
    def NOTEBOOKS(request, params):
        """Delegate to notebook manager; handles notebook CRUD and strokes."""
        cls = getattr(notebook_manager, NOTEBOOK_MANAGER_CLASS_NAME)
        return getattr(cls, request)(params)

    @staticmethod
    def USERS_NOTEBOOKS(request, params):
        """Delegate to user-notebook manager; links users to notebooks."""
        cls = getattr(user_notebook_manager, USER_NOTEBOOK_MANAGER_CLASS_NAME)
        return getattr(cls, request)(params)
