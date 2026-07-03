import websockets

async def client():
    uri = "ws://localhost:8765"
    # 1, 打开 websocket 连接
    async with websockets.connect(uri) as websocket:
        # 2, 发送消息
        await websocket.send("Hello, WebSocket!")
        # 3, 接收服务器返回的消息
        response = await websocket.recv()
        print(f"Received from server: {response}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(client())