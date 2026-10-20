"""Provider seam and a deterministic fake so everything runs offline."""

from dataclasses import dataclass, field
from typing import List, Protocol


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class Request:
    messages: List[Message]


@dataclass(frozen=True)
class Response:
    content: str


class Provider(Protocol):
    def complete(self, request: Request) -> Response: ...


@dataclass
class FakeProvider:
    """Echoes the last user message and records what it was actually sent."""

    seen: List[Request] = field(default_factory=list)

    def complete(self, request: Request) -> Response:
        self.seen.append(request)
        return Response(f"You said: {request.messages[-1].content}")
