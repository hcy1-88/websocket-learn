import json
import asyncio
from collections.abc import AsyncIterator, Iterable
from typing import Any
from uuid import uuid4

from websockets.asyncio.server import ServerConnection


class WsConnection:
    """对 WebSocket connection 进行封装和增强."""

    def __init__(self, raw_websocket: ServerConnection) -> None:
        self.raw = raw_websocket
        self.id: str = uuid4().hex
        self.current_req_id: str | None = None

    @property
    def remote_address(self):
        return self.raw.remote_address

    @property
    def request(self):
        return self.raw.request

    async def send_event(self, event_name: str, data: dict[str, Any] | None = None, req_id: str | None = None) -> None:
        """统一正常消息发送"""
        message = {
            "event": event_name,
            "data": data or {},
            "error": None,
            "req_id": req_id or self.current_req_id,
        }
        await self.raw.send(json.dumps(message, ensure_ascii=False))

    async def send_error(self, message: str, event_name: str = "error", req_id: str | None = None) -> None:
        """统一错误消息发送"""
        payload = {
            "event": event_name,
            "data": {},
            "error": message,
            "req_id": req_id or self.current_req_id,
        }
        await self.raw.send(json.dumps(payload, ensure_ascii=False))

    @staticmethod
    async def broadcast(connections: Iterable["WsConnection"], event_name: str, data: dict[str, Any]) -> None:
        """广播给指定 ws 集合"""
        connections = set(connections)
        if not connections:
            return

        await asyncio.gather(
            *(connection.send_event(event_name, data, req_id=None) for connection in connections.copy()),
            return_exceptions=True,
        )

    async def close(self, code: int = 1000, reason: str = "") -> None:
        """关闭 ws 连接"""
        await self.raw.close(code=code, reason=reason)

    async def iter_payloads(self) -> AsyncIterator[dict[str, Any]]:
        """从 websocket 连接中迭代接收消息, yield JSON 对象"""
        async for raw_message in self.raw:
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                await self.send_error("message must be valid JSON")
                continue

            req_id = payload.get("req_id")
            self.current_req_id = req_id if isinstance(req_id, str) else None
            yield payload
            self.current_req_id = None
