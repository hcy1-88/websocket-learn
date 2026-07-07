from collections.abc import Awaitable, Callable

from websockets.asyncio.server import ServerConnection

from core.event_router import EventRouter


# 任何 “接收一个 ServerConnection 参数，并返回一个 awaitable，最终结果是 None” 的可调用对象，都算 WebSocketHandler
WebSocketHandler = Callable[[ServerConnection], Awaitable[None]]


class UrlRouter:
    """URL 层路由，读取 websocket 请求的 URL Path，分发到对应的 handler"""

    def __init__(self) -> None:
        self.routes: dict[str, WebSocketHandler] = {}

    def add_route(self, path: str, handler: WebSocketHandler) -> None:
        self.routes[path] = handler

    def add_event_router(self, event_router: EventRouter) -> None:
        """一个路径，一个 handler"""
        self.add_route(event_router.full_path, event_router.connect)

    async def dispatch(self, websocket: ServerConnection) -> None:
        path = websocket.request.path
        handler = self.routes.get(path)

        if handler is None:
            await websocket.close(code=1008, reason=f"unknown websocket path: {path}")
            return

        await handler(websocket)
