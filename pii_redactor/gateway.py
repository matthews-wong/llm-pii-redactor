"""Redact on the way out, restore on the way back."""

from dataclasses import replace
from typing import Dict

from .provider import Message, Provider, Request, Response
from .redactor import Redactor, restore


class RedactingGateway:
    def __init__(self, provider: Provider, redactor: Redactor = None) -> None:
        self._provider = provider
        self._redactor = redactor or Redactor()

    def complete(self, request: Request) -> Response:
        # One mapping per request so placeholders agree across messages and
        # nothing is retained after the call returns.
        mapping: Dict[str, str] = {}
        messages = [
            Message(m.role, self._redactor.redact(m.content, mapping).text)
            for m in request.messages
        ]
        response = self._provider.complete(replace(request, messages=messages))
        return Response(restore(response.content, mapping))
