import os
import sys
from datetime import datetime
from typing import Any, Literal, Union

import grpc
import requests

from groq.cloud.core.auth import Auth
from groq.cloud.core.exceptions import *
from groq.cloud.core.types import GroqListModelsResponse
from public.llmcloud.modelmanager.v1 import modelmanager_pb2, modelmanager_pb2_grpc
from public.llmcloud.requestmanager.v1 import (
    requestmanager_pb2,
    requestmanager_pb2_grpc,
)


class GroqGrpcConnection:
    _grpc_channel = None
    _grpc_channel_async = None
    _auth_token = ""
    _auth_expiry_time = ""
    _API_URL = "api.groq.com:443"
    auth_client: Auth

    def _get_grpc_credentials(self):
        self._auth_token = self.auth_client.get_token()

        credentials = grpc.ssl_channel_credentials()
        call_credentials = grpc.access_token_call_credentials(self._auth_token)
        credentials = grpc.composite_channel_credentials(credentials, call_credentials)
        return credentials

    def _open_grpc_channel(self) -> grpc.secure_channel:
        credentials = self._get_grpc_credentials()
        query_channel = grpc.secure_channel(self._API_URL, credentials)
        return query_channel

    def _open_grpc_channel_async(self) -> grpc.aio.secure_channel:
        credentials = self._get_grpc_credentials()
        query_channel = grpc.aio.secure_channel(self._API_URL, credentials)
        return query_channel

    def __init__(self):
        self.auth_client = Auth()

    def __del__(self):
        if self._grpc_channel is not None:
            self._grpc_channel.close()
            self._grpc_channel = None

    def get_grpc_channel(self):
        if self._grpc_channel is None:
            self._grpc_channel = self._open_grpc_channel()

        return self._grpc_channel

    async def __aexit__(self):
        if self._grpc_channel_async is not None:
            self._grpc_channel_async.aio.close()
            self._grpc_channel_async = None

    def get_grpc_channel_async(self):
        if self._grpc_channel_async is None:
            self._grpc_channel_async = self._open_grpc_channel_async()

        return self._grpc_channel_async


grpc_connection = GroqGrpcConnection()


class Models:
    def __init__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        self._stub = modelmanager_pb2_grpc.ModelManagerServiceStub(self._query_channel)

    def list_models(self):
        request = modelmanager_pb2.ListModelsRequest()
        resp = self._stub.ListModels(request)

        models = []

        try:
            for model in resp.models:
                details = GroqListModelsResponse.Details(
                    family=model.details.family,
                    version=model.details.version,
                    size=model.details.size,
                    sequence_length=model.details.sequence_length,
                    tag=model.details.tag,
                    name=model.details.name,
                    owner=model.details.owner,
                )
                meta = GroqListModelsResponse.Meta(created=model.meta.created)
                response = GroqListModelsResponse(
                    id=model.id,
                    details=details,
                    meta=meta,
                    status=model.status,
                )

                models.append(response)
        except Exception as e:
            raise e

        return models


class ChatCompletion:
    def __init__(self, model):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(
            self._query_channel
        )
        self._model = model
        self._system_prompt = "Give useful and accurate answers."
        self._lastmessages = []
        self._history_index = 0

    def __del__(self):
        self._lastmessages = []

    def __enter__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        return self

    def __exit__(self, *args: object) -> None:
        self._lastmessages = []
        return None

    def _update_history(self, user_prompt, response):
        self._lastmessages.append({"user_prompt": user_prompt, "last_resp": response})

    def _resp_generator(self, resp_stream):
        for response in resp_stream:
            self._lastmessages[-1]["last_resp"] += response.content
            yield response

    def clear_history(self):
        self._lastmessages = []

    def update_history(self, history_pairs):
        for pair in history_pairs:
            self._update_history(pair[0], pair[1])

    def set_system_prompt(self, system_prompt):
        self._system_prompt = system_prompt

    def send_chat(
        self,
        user_prompt="Write multiple paragraphs",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[""], Literal[""], dict], Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt

        history_messages = -1
        for msg in self._lastmessages:
            history_messages += 1
            req = request.history.add()
            req.user_prompt = msg["user_prompt"]
            req.assistant_response = msg["last_resp"]

        self._history_index = history_messages

        request.model_id = self._model
        request.system_prompt = self._system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(e)
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ModelUnavailableError(e)
            else:
                raise e

        if streaming == True:
            self._update_history(user_prompt, "")
            return self._resp_generator(resp_stream=resp_stream)
        else:
            self._update_history(user_prompt, resp.content)
            return resp.content, resp.request_id, resp.stats


class Completion:
    def __init__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(
            self._query_channel
        )

    def __del__(self):
        return

    def __enter__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel()
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def _resp_generator(self, resp_stream):
        for response in resp_stream:
            yield response

    def send_prompt(
        self,
        model,
        user_prompt="Write multiple paragraphs",
        system_prompt="Give useful and accurate answers.",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[""], Literal[""], dict], Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt
        request.model_id = model
        request.system_prompt = system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(e)
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ModelUnavailableError(e)
        except grpc._channel._MultiThreadedRendezvous as e:
            # TODO: this is broken somehow, as if what is being raised isn't an exception?
            raise InvalidArgumentError(e)
        except Exception as e:
            raise e

        if streaming == True:
            return self._resp_generator(resp_stream=resp_stream)
        else:
            return resp.content, resp.request_id, resp.stats


class AsyncCompletion:
    def __init__(
        self,
        model,
        user_prompt="Write multiple paragraphs",
        system_prompt="Give useful and accurate answers.",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ):
        global grpc_connection
        self._query_channel_async = grpc_connection.get_grpc_channel_async()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(
            self._query_channel_async
        )

    async def __aenter__(self):
        global grpc_connection
        self._query_channel_async = grpc_connection.get_grpc_channel_async()
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def _resp_generator(self, resp_stream):
        async for response in resp_stream:
            yield response

    async def send_prompt(
        self,
        model,
        user_prompt="Write multiple paragraphs",
        system_prompt="Give useful and accurate answers.",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[""], Literal[""], dict], Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt
        request.model_id = model
        request.system_prompt = system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = await self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(e)
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ModelUnavailableError(e)
            else:
                raise e

        if streaming == True:
            return self._resp_generator(resp_stream=resp_stream)
        else:
            return resp.content, resp.request_id, resp.stats


class AsyncChatCompletion:
    def __init__(self, model):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel_async()
        self._stub = requestmanager_pb2_grpc.RequestManagerServiceStub(
            self._query_channel
        )
        self._model = model
        self._system_prompt = "Give useful and accurate answers."
        self._lastmessages = []
        self._history_index = 0

    def __del__(self):
        self._lastmessages = []

    async def __aenter__(self):
        global grpc_connection
        self._query_channel = grpc_connection.get_grpc_channel_async()
        return self

    async def __aexit__(self, *args: object) -> None:
        self._lastmessages = []
        return None

    def _update_history(self, user_prompt, response):
        self._lastmessages.append({"user_prompt": user_prompt, "last_resp": response})

    async def _resp_generator(self, resp_stream):
        async for response in resp_stream:
            if self._history_index > -1:
                self._lastmessages[self._history_index]["last_resp"] += response.content
            yield response

    async def send_chat(
        self,
        user_prompt="Write multiple paragraphs",
        streaming=False,
        seed=1234,
        max_tokens=2048,
        temperature=0.7,
        top_p=0.3,
        top_k=40,
    ) -> Union[tuple[Literal[""], Literal[""], dict], Any]:
        # Generate request
        request = requestmanager_pb2.GetTextCompletionRequest()
        request.user_prompt = user_prompt

        history_messages = -1
        for msg in self._lastmessages:
            history_messages += 1
            req = request.history.add()
            req.user_prompt = msg["user_prompt"]
            req.assistant_response = msg["last_resp"]

        self._history_index = history_messages

        request.model_id = self._model
        request.system_prompt = self._system_prompt
        request.seed = seed
        request.max_tokens = max_tokens
        request.temperature = temperature
        request.top_p = top_p
        request.top_k = top_k

        try:
            if streaming == True:
                resp_stream = self._stub.GetTextCompletionStream(request)
            else:
                resp = await self._stub.GetTextCompletion(request)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise InvalidArgumentError(e)
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ModelUnavailableError(e)
            else:
                raise e

        if streaming == True:
            self._update_history(user_prompt, "")
            return self._resp_generator(resp_stream=resp_stream)
        else:
            self._update_history(user_prompt, resp.content)
            return resp.content, resp.request_id, resp.stats
