"""
This module defines custom exception for CTFd-chall-manager plugin.
"""


from __future__ import annotations

import json
from typing import Any

import requests

# Mapping derived from gRPC to HTTP status recommendations
GRPC_STATUS_TO_HTTP = {
    0: 200,  # OK
    1: 499,  # CANCELLED
    2: 500,  # UNKNOWN
    3: 400,  # INVALID_ARGUMENT
    4: 504,  # DEADLINE_EXCEEDED
    5: 404,  # NOT_FOUND
    6: 409,  # ALREADY_EXISTS
    7: 403,  # PERMISSION_DENIED
    8: 429,  # RESOURCE_EXHAUSTED
    9: 400,  # FAILED_PRECONDITION
    10: 409,  # ABORTED
    11: 400,  # OUT_OF_RANGE
    12: 501,  # UNIMPLEMENTED
    13: 500,  # INTERNAL
    14: 503,  # UNAVAILABLE
    15: 500,  # DATA_LOSS
    16: 401,  # UNAUTHENTICATED
}


class ChallManagerException(Exception):
    """
    This class handles errors returns by Chall-Manager API.
    """

    def __init__(
        self,
        code: int | None = 2,
        message: str = "An error occurred",
        details: Any | None = None,
        http_status: int | None = 500,
    ):
        self.code = code
        self.message = message
        self.details = details or []
        self.http_status = http_status or 500
        super().__init__(self.message)

    def __str__(self):
        details_str = f", details: {self.details}" if self.details else ""
        return (
            f"ChallManagerError(code={self.code}, message='{self.message}', "
            f"http_status={self.http_status}{details_str})"
        )


def grpc_to_http_status(grpc_code: int | None, fallback: int) -> int:
    """
    Translate a gRPC status code into an HTTP status code.
    """
    if grpc_code is None:
        return fallback
    return GRPC_STATUS_TO_HTTP.get(grpc_code, fallback)


def build_cm_exception(
    response: requests.Response | None,
    default_message: str,
    *,
    fallback_status: int = 500,
) -> ChallManagerException:
    """
    Convert a Chall-Manager HTTP response (gRPC gateway) into a ChallManagerException.

    The gRPC gateway always returns an HTTP response, sometimes with a body
    containing ``code``/``message``/``details`` fields. This helper extracts the
    meaningful parts so that callers can propagate them to users.
    """
    if response is None:
        return ChallManagerException(
            message=default_message,
            http_status=fallback_status,
        )

    message = default_message
    details: Any | None = None
    grpc_code: int | None = None

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        message = payload.get("message") or payload.get("error") or message
        details = payload.get("details")

        try:
            grpc_code = int(payload.get("code"))
        except (TypeError, ValueError):
            grpc_code = None
    else:
        # Fallback to raw body
        text = response.text.strip()
        if text:
            try:
                payload = json.loads(text)
                if isinstance(payload, dict):
                    message = payload.get("message") or payload.get("error") or message
                    details = payload.get("details")
                    try:
                        grpc_code = int(payload.get("code"))
                    except (TypeError, ValueError):
                        grpc_code = None
                else:
                    message = text
            except json.JSONDecodeError:
                message = text

    http_status = grpc_to_http_status(
        grpc_code, response.status_code or fallback_status
    )

    return ChallManagerException(
        code=grpc_code if grpc_code is not None else response.status_code,
        message=message,
        details=details,
        http_status=http_status,
    )


def build_error_payload(exc: ChallManagerException) -> tuple[dict[str, Any], int]:
    """
    Standardize the error payload returned by API endpoints.
    """
    data: dict[str, Any] = {"message": exc.message}
    if exc.code is not None:
        data["code"] = exc.code
    if exc.details:
        data["details"] = exc.details

    return data, exc.http_status
