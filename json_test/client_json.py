import json

import websockets


async def client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # 转发 json
        data = json.dumps({"id": 1, "name": "张三", "operation": "delete"}, ensure_ascii=False)
        await websocket.send(data)
        # 接收响应
        response = await websocket.recv()
        # json 转字典
        response_data = json.loads(response)
        print(f"Received from server: {response_data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(client())
