import asyncio

from core.server import WsServer
from routers.chat import chat_router
from routers.market import market_router


def create_server() -> WsServer:
    server = WsServer(host="localhost", port=8765)
    server.add_event_routers(chat_router, market_router)

    @server.before_server_start
    async def init_resources(server: WsServer) -> None:
        print("[before_server_start] 初始化数据库、Redis、后台任务等资源")

    @server.after_server_start
    async def report_ready(server: WsServer) -> None:
        print(f"[after_server_start] 服务已就绪: ws://{server.host}:{server.port}")

    @server.before_server_stop
    async def stop_background_jobs(server: WsServer) -> None:
        print("[before_server_stop] 停止后台任务，准备关闭连接")

    @server.listener("after_server_stop")
    async def release_resources(server: WsServer) -> None:
        print("[after_server_stop] 释放数据库连接、刷新日志")

    return server


async def main() -> None:
    # 启动方式一：
    server = create_server()
    await server.serve_forever()
    
    # 启动方式二：
    # async with create_server():
    #     await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
