import json

from sanic import Sanic
from sanic.response import json as json_response

app = Sanic(name="websocket_demo")
app.config.update(
    {
        # 单个 HTTP 请求体最大字节数，这里约 10MB。
        "REQUEST_MAX_SIZE": 10000000,
        # HTTP 请求读取超时时间，单位秒。
        "REQUEST_TIMEOUT": 120,
        # HTTP 响应发送超时时间，单位秒。
        "RESPONSE_TIMEOUT": 120,
        # 是否启用 HTTP keep-alive，允许复用 TCP 连接。
        "KEEP_ALIVE": True,
        # 是否打印访问日志；demo 里关掉，减少控制台噪音。
        "ACCESS_LOG": False,
        # 单条 WebSocket 消息最大字节数，这里是 32MB。
        "WEBSOCKET_MAX_SIZE": 2**25,
        # WebSocket ping 心跳间隔，单位秒。
        "WEBSOCKET_PING_INTERVAL": 60,
        # WebSocket ping 超时时间，超过后认为连接不可用。
        "WEBSOCKET_PING_TIMEOUT": 180,
    }
)


async def login(request):
    body = request.json or {}
    username = body.get("username", "游客")
    return json_response(
        {
            "message": "登录成功",
            "code": 200,
            "token": f"demo-token-{username}",
        }
    )


async def send_event(ws, event_name: str, data: dict | None = None, req_id: str | None = None) -> None:
    await ws.send(
        json.dumps(
            {
                "event": event_name,
                "data": data or {},
                "error": None,
                "req_id": req_id,
            },
            ensure_ascii=False,
        )
    )


async def send_error(ws, message: str, req_id: str | None = None) -> None:
    await ws.send(
        json.dumps(
            {
                "event": "error",
                "data": {},
                "error": message,
                "req_id": req_id,
            },
            ensure_ascii=False,
        )
    )


async def chat_ws(request, ws):
    token = request.args.get("token")
    if not token:
        await send_error(ws, "missing token")
        await ws.close()
        return

    print(f"WebSocket connected: token={token}")
    await send_event(ws, "chat.connected", {"message": "WebSocket 连接成功"})

    try:
        # 迭代消息
        async for raw_message in ws:
            try:
                # 转 json
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                await send_error(ws, "message must be valid JSON")
                continue
            # 处理事件
            event_name = payload.get("event")
            data = payload.get("data", {})
            req_id = payload.get("req_id")

            if event_name == "chat.ping":
                await send_event(ws, "chat.pong", {"message": "pong"}, req_id)
            elif event_name == "chat.send":
                text = data.get("text") if isinstance(data, dict) else None
                if not text:
                    await send_error(ws, "text is required", req_id)
                    continue
                await send_event(ws, "chat.message", {"from": "server", "text": "收到了：" + text}, req_id)
            elif event_name == "chat.close":
                await send_event(ws, "chat.closed", {"message": "服务端准备关闭连接"}, req_id)
                await ws.close()
                return
            else:
                await send_error(ws, f"unknown event: {event_name}", req_id)
    finally:
        print(f"WebSocket disconnected: token={token}")

# 添加 http 路由
app.add_route(login, "/login", methods=["POST"])

# 添加 websocket 路由
app.add_websocket_route(chat_ws, "/ws/chat")


if __name__ == "__main__":
    app.run(host="localhost", port=8765, single_process=True)
