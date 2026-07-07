import asyncio
import websockets

from collections.abc import Awaitable, Callable
from websockets.asyncio.server import Server, ServerConnection
from core.event_router import EventRouter
from core.url_router import UrlRouter


ServerListener = Callable[["WsServer"], Awaitable[None]]


class WsServer:
    """WebSocket server, 负责启动 WebSocket 服务，管理 URL 路由和事件路由。"""

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.url_router = UrlRouter()
        self._server: Server | None = None
        self._stop_event = asyncio.Event()
        self._listeners: dict[str, list[ServerListener]] = {
            "before_server_start": [],
            "after_server_start": [],
            "before_server_stop": [],
            "after_server_stop": [],
        }

    def add_event_router(self, event_router: EventRouter) -> None:
        """添加事件路由"""
        self.url_router.add_event_router(event_router)

    def add_event_routers(self, *event_routers: EventRouter) -> None:
        """添加多个事件路由"""
        for event_router in event_routers:
            self.add_event_router(event_router)

    # 装饰器，可 `@server.listener("before_server_start")` 声明监听器
    def listener(self, event_name: str):
        """注册服务生命周期监听器。"""
        if event_name not in self._listeners:
            raise ValueError(f"unknown server listener event: {event_name}")

        def decorator(func: ServerListener) -> ServerListener:
            self._listeners[event_name].append(func)
            return func

        return decorator

    # 装饰器，可 `@server.before_server_start` 直接声明监听器
    def before_server_start(self, func: ServerListener) -> ServerListener:
        return self.listener("before_server_start")(func)

    def after_server_start(self, func: ServerListener) -> ServerListener:
        return self.listener("after_server_start")(func)

    def before_server_stop(self, func: ServerListener) -> ServerListener:
        return self.listener("before_server_stop")(func)

    def after_server_stop(self, func: ServerListener) -> ServerListener:
        return self.listener("after_server_stop")(func)

    async def run_listeners(self, event_name: str) -> None:
        for listener in self._listeners[event_name]:
            await listener(self)

    async def handler(self, websocket: ServerConnection) -> None:
        """"处理 WebSocket 连接请求，分发到对应的 URL 路由"""
        await self.url_router.dispatch(websocket)

    async def start(self) -> None:
        """启动 WebSocket 服务"""
        await self.run_listeners("before_server_start")
        self._server = await websockets.serve(self.handler, self.host, self.port)
        self.print_routes()
        await self.run_listeners("after_server_start")

    async def stop(self) -> None:
        """停止 WebSocket 服务"""
        if self._server is None:
            return

        await self.run_listeners("before_server_stop")
        self._server.close()
        await self._server.wait_closed()
        self._server = None
        self._stop_event.set()
        await self.run_listeners("after_server_stop")

    async def serve_forever(self) -> None:
        await self.start()

        try:
            await self._stop_event.wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            await self.stop()
            print("WebSocket 服务已停止.")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.stop()

    def print_routes(self) -> None:
        print("WebSocket server started:")
        for path in self.url_router.routes:
            print(f"  {path} -> ws://{self.host}:{self.port}{path}")
