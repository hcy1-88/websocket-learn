import websockets


async def client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            # 接收响应
            response = await websocket.recv()
            print(f"Received from server: {response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(client())