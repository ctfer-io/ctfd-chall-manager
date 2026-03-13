"""
This module defines custom exception for CTFd-chall-manager plugin.
"""

import json

import requests
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger

logger = configure_logger(__name__)


class ChallManagerException(Exception):
    """
    This class handles errors returns by Chall-Manager API.
    """

    def __init__(self, code=2, message="An error occurred", details=None):
        self.code = code
        self.message = message
        self.details = (
            details or []
        )  # Default to an empty list if no details are provided
        super().__init__(self.message)

    def __str__(self):
        details_str = f", details: {self.details}" if self.details else ""
        return f"ChallManagerException(code={self.code}, message='{self.message}'{details_str})"


def chall_manager_exception_builder(resp: requests.Response) -> ChallManagerException:
    """
    Helper function to create internal exception based on Chall-Manager API response
    """

    cm_error = json.loads(resp.text)
    cm_exception = ChallManagerException(
        code=cm_error["code"], message=cm_error["message"], details=cm_error["details"]
    )

    return cm_exception
