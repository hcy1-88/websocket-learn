from collections.abc import Awaitable, Callable
from typing import Any
from core.connection import WsConnection
from websockets.asyncio.server import ServerConnection


EventHandler = Callable[[WsConnection, dict[str, Any]], Awaitable[None]]


class EventRouter:
    """事件层路由：一个 EventRouter 对应一个 WebSocket URL 入口。"""

    def __init__(self, prefix: str, path: str) -> None:
        self.prefix: str = prefix.strip("/")
        self.path: str = path.strip("/")
        self.full_path: str = f"/{self.prefix}/{self.path}"
        self.handlers: dict[str, EventHandler] = {}
        self.clients: set[WsConnection] = set()
        self.state: dict[str, object] = {}

    def on(self, event_name: str):
        """装饰器 - 注册事件"""
        def decorator(handler: EventHandler) -> EventHandler:
            self.handlers[event_name] = handler
            return handler

        return decorator

    async def broadcast(self, event_name: str, data: dict[str, Any]) -> None:
        await WsConnection.broadcast(self.clients, event_name, data)

    async def dispatch(self, connection: WsConnection, payload: dict[str, Any]) -> None:
        """分发消息"""
        event_name = payload.get("event")
        data = payload.get("data", {})

        if not isinstance(event_name, str) or not event_name:
            await connection.send_error("missing event")
            return

        if not isinstance(data, dict):
            await connection.send_error("data must be an object")
            return

        handler = self.handlers.get(event_name)
        if handler is None:
            await connection.send_error(f"未知的消息事件，路径：{self.full_path} - 事件名称: {event_name}")
            return

        await handler(connection, data)

    async def connect(self, raw_websocket: ServerConnection) -> None:
        connection = WsConnection(raw_websocket)
        self.clients.add(connection)
        print(f"connected: {self.full_path} - {connection.remote_address}")

        try:
            await connection.send_event(
                f"{self.path}.connected",
                {
                    "connection_id": connection.id,
                    "message": f"connected to {self.full_path}",
                },
            )
            await self.read_messages(connection)
        finally:
            self.clients.discard(connection)
            await self.cleanup(connection)
            print(f"disconnected: {self.full_path} - {connection.remote_address}")

    async def cleanup(self, connection: WsConnection) -> None:
        """子类或调用方可按需覆盖；demo 里直接通过 state 做清理。"""
        pass

    async def read_messages(self, connection: WsConnection) -> None:
        async for payload in connection.iter_payloads():
            await self.dispatch(connection, payload)
