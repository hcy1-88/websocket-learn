import asyncio
import json
from urllib import request

import websockets


def login(username: str, password: str) -> str:
    body = json.dumps(
        {
            "username": username,
            "password": password,
        },
        ensure_ascii=False,
    ).encode("utf-8")

    http_request = request.Request(
        "http://localhost:8765/login",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(http_request) as response:
        payload = json.loads(response.read().decode("utf-8"))

    token = payload.get("token")
    if not isinstance(token, str) or not token:
        raise RuntimeError(f"login response missing token: {payload}")
    return token


async def send_json(websocket, event_name: str, data: dict | None = None) -> None:
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


async def recv_and_print(websocket, label: str) -> None:
    message = await websocket.recv()
    print(f"[{label}] {message}")


async def main() -> None:
    token = login("alice", "123456")
    print(f"[login] token={token}")

    uri = f"ws://localhost:8765/ws/chat?token={token}"

    async with websockets.connect(uri) as websocket:
        await recv_and_print(websocket, "connected")

        await send_json(websocket, "chat.ping")
        await recv_and_print(websocket, "ping")

        await send_json(websocket, "chat.send", {"text": "你好，Sanic WebSocket"})
        await recv_and_print(websocket, "chat")

        await send_json(websocket, "chat.close")
        await recv_and_print(websocket, "close")


if __name__ == "__main__":
    asyncio.run(main())