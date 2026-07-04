import asyncio

import websockets


async def handler(websocket):
    async for message in websocket:
        # 接收消息
        if message == "close":
            # 主动关闭连接（标准关闭码 1000：正常关闭）
            await websocket.close(code=1000, reason="客户端请求关闭")
            print(f"连接已关闭（错误码：{websocket.close_code}，原因：{websocket.close_reason}）")
        else:
            print(f"收到消息: {message}")
            await websocket.send("收到!")

async def main():
    async with websockets.serve(handler, "localhost", 8767):
        print("WebSocket 服务启动在 ws://localhost:8767")
        await asyncio.Future()  # 永不退出


if __name__ == "__main__":
    asyncio.run(main())
