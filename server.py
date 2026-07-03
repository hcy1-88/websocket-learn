
import asyncio

import websockets


async def echo(websocket):
    """处理 websocket 消息"""
    path = websocket.request.path
    # ws 消息监听和遍历
    async for message in websocket:
        print(f"path: {path} - 收到消息: {message}")  # path: / - 收到消息: Hello, WebSocket!
        await websocket.send("Hello from server!")


async def main():
    # 启动 websocket 服务（此方法返回一个 server，内部实现了 aenter 和 aexit 所以可以使用 async with）
    async with websockets.serve(echo, "localhost", 8765):
        print("WebSocket 服务启动在 ws://localhost:8765")
        # 永不退出
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
