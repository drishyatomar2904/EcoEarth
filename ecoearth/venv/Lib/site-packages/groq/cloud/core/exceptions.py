from __future__ import annotations

from typing import Any, Optional, cast

import grpc
from typing_extensions import Literal


class GroqError(Exception):
    pass


class APIError(GroqError):
    message: str
    error_code: Optional[Literal]
    # body: object | None

    def __init__(self, message: str, error_code=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class APIStatusError(APIError):
    """Raised when an API response has a status code of 4xx or 5xx, or is in Maintenance mode"""

    pass


class AuthenticationError(APIStatusError):
    status_code: Literal[401] = 401
    message = "Token is invalid for this request"

    def __init__(self):
        super().__init__(message=self.message)


class RateLimitError(APIStatusError):
    status_code: Literal[429] = 429


class APIMaintenanceMode(APIStatusError):
    status_code: Literal[404] = 404
    error_code: Literal[9999] = 9999


class QueueFullError(APIStatusError):
    status_code: Literal[503] = 503
    error_code: Literal[14] = 14


class PlaceInQueueError(APIStatusError):
    status_code: Literal[404] = 404
    error_code: Literal[5] = 5


class InvalidArgumentError(APIError):
    def __init__(self, e: grpc.RpcError):
        super().__init__(
            message="Invalid Args. Please check model name and other parameters"
        )


class ModelUnavailableError(APIError):
    def __init__(self, e: grpc.RpcError):
        super().__init__(message="Requested model maybe currently offline")


class AuthTokenError(APIError):
    def __init__(self):
        super().__init__(
            message="Key not found. Please set env variable GROQ_SECRET_ACCESS_KEY with the unique secret"
        )


# except grpc.RpcError as e:
#             if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
#                 print("Invalid Args. Please check model name and other params")
#             elif e.code() == grpc.StatusCode.UNAVAILABLE:
#                 print(
#                     f"grpc error: {e.details()}. Requested model maybe currently offline."
#                 )
#             else:
#                 raise e
#             return "", "", {}
