import os

from groq.cloud.core.exceptions import AuthTokenError
import requests


class Auth:
    _grpc_channel = None
    _grpc_channel_async = None
    _groq_access_key = ""
    _VALIDATION_URL = "https://api.groq.com/v1/request_manager/ping"

    def __init__(self):
        return

    def _verify_token_validity(self):
        headers = {
            "Authorization": "Bearer " + self._groq_access_key,
        }

        try:
            auth_resp = requests.post(url=self._VALIDATION_URL, headers=headers)
            if not auth_resp.status_code == 404:
                raise AuthTokenError
        except Exception:
            raise AuthTokenError

        return True

    def get_token(self):
        self._groq_access_key = os.environ.get("GROQ_SECRET_ACCESS_KEY")
        try:
            self._verify_token_validity()
        except Exception:
            raise AuthTokenError

        return self._groq_access_key
