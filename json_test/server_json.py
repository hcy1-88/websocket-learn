import json
import asyncio
import websockets


async def handler(websocket):
    async for message in websocket:
        # json 转字典
        data = json.loads(message)
        print(f"收到消息: {data}")
        response = {"status": "success", "message": "操作成功！"}
        # 发 json 响应
        await websocket.send(json.dumps(response, ensure_ascii=False))

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket 服务启动在 ws://localhost:8765")
        await asyncio.Future()  # 永不退出


if __name__ == "__main__":
    asyncio.run(main())
