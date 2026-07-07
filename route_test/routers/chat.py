from core.connection import WsConnection
from core.event_router import EventRouter


chat_router = EventRouter(prefix="ws", path="chat")


@chat_router.on("chat.send")
async def handle_chat_send(connection: WsConnection, data: dict) -> None:
    text = data.get("text")
    if not text:
        await connection.send_error("chat.send requires data.text")
        return

    await chat_router.broadcast(
        "chat.message",
        {
            "from": str(connection.remote_address),
            "text": text,
        },
    )


@chat_router.on("chat.ping")
async def handle_chat_ping(connection: WsConnection, data: dict) -> None:
    await connection.send_event("chat.pong", {"message": "chat ok"})
