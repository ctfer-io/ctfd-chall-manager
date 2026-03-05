"""
This module register API endpoints for the plugin in CTFd (/api/v1).
"""

from CTFd.api import CTFd_API_v1
from ..api.admin.instance import AdminInstance
from ..api.instance import UserInstance
from ..api.mana import UserMana
from ..utils.logger import configure_logger
from flask_restx import Namespace

# Configure logger for this module
logger = configure_logger(__name__)

admin_namespace = Namespace("ctfd-chall-manager-admin")
user_namespace = Namespace("ctfd-chall-manager-user")


@admin_namespace.errorhandler
@user_namespace.errorhandler
def handle_default(err):
    """
    Handler for namespaces error
    """
    logger.error("Unexpected error: %s", err)
    return {"success": False, "message": "Unexpected things happened"}, 500


def register_api_endpoints():
    """
    Add namespaces of the CTFd-chall-manager plugin in CTFd /api/v1/plugins
    """
    # add resources to namespaces
    admin_namespace.add_resource(AdminInstance, "/instance")
    user_namespace.add_resource(UserInstance, "/instance")
    user_namespace.add_resource(UserMana, "/mana")

    # register namespace in CTFd
    CTFd_API_v1.add_namespace(admin_namespace, path="/plugins/ctfd-chall-manager/admin")
    CTFd_API_v1.add_namespace(user_namespace, path="/plugins/ctfd-chall-manager")
