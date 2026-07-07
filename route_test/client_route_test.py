import asyncio
import json

import websockets


async def send_json(websocket, event_name, data=None):
    await websocket.send(
        json.dumps(
            {
                "req_id": f"req-{event_name}",
                "event": event_name,
                "data": data or {},
            },
            ensure_ascii=False,
        )
    )


async def recv_and_print(websocket, label):
    message = await websocket.recv()
    print(f"[{label}] {message}")


async def chat_demo():
    async with websockets.connect("ws://localhost:8765/ws/chat") as websocket:
        # 1. 连接后，服务端会发送一条 chat.connected 消息
        await recv_and_print(websocket, "chat")

        # 2. 发送 ping 消息，服务端会返回 chat.pong 消息
        await send_json(websocket, "chat.ping")
        await recv_and_print(websocket, "chat")

        # 3. 发送聊天消息，服务端会返回 chat.message 消息
        await send_json(websocket, "chat.send", {"text": "你好，聊天室"})
        await recv_and_print(websocket, "chat")


async def market_demo():
    async with websockets.connect("ws://localhost:8765/ws/market") as websocket:
        # 1. 连接后，服务端会发送一条 chat.connected 消息
        await recv_and_print(websocket, "market")

        # 2. 订阅行情
        await send_json(websocket, "market.subscribe", {"symbol": "BTC-USDT"})
        # - 收到 market.subscribed 消息
        await recv_and_print(websocket, "market")

        # 3. 推送行情
        await send_json(websocket, "market.quote", {"symbol": "BTC-USDT", "price": 65000})

        # 4. 收到广播
        await recv_and_print(websocket, "market")


async def main():
    await chat_demo()
    await market_demo()


if __name__ == "__main__":
    asyncio.run(main())