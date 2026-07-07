from collections import defaultdict
from core.connection import WsConnection
from core.event_router import EventRouter


class MarketRouter(EventRouter):
    """市场行情路由"""

    def __init__(self, prefix: str, path: str) -> None:
        """
        market_router.state 示例：
        {
            "subscribers": {
                "BTC-USDT": {connection_1, connection_3},
                "ETH-USDT": {connection_2},
            }
        }
        """
        super().__init__(prefix, path)
        self.state["subscribers"] = defaultdict(set)
        
    
    async def cleanup(self, connection: WsConnection) -> None:
        """连接断开时，从所有行情订阅集合中移除该连接。"""
        subscribers = self.state["subscribers"]
        for connections in subscribers.values():
            connections.discard(connection)


market_router = MarketRouter(prefix="ws", path="market")


@market_router.on("market.subscribe")
async def handle_market_subscribe(connection: WsConnection, data: dict) -> None:
    """订阅行情"""
    symbol = data.get("symbol")
    if not symbol:
        await connection.send_error("market.subscribe requires data.symbol")
        return

    subscribers = market_router.state["subscribers"]
    subscribers[symbol].add(connection)
    await connection.send_event("market.subscribed", {"symbol": symbol})


@market_router.on("market.unsubscribe")
async def handle_market_unsubscribe(connection: WsConnection, data: dict) -> None:
    """取消订阅行情"""
    symbol = data.get("symbol")
    if not symbol:
        await connection.send_error("market.unsubscribe requires data.symbol")
        return

    subscribers = market_router.state["subscribers"]
    subscribers[symbol].discard(connection)
    await connection.send_event("market.unsubscribed", {"symbol": symbol})


@market_router.on("market.quote")
async def handle_market_quote(connection: WsConnection, data: dict) -> None:
    """行情推送"""
    symbol = data.get("symbol")
    price = data.get("price")

    if not symbol or price is None:
        await connection.send_error("market.quote requires data.symbol and data.price")
        return

    subscribers = market_router.state["subscribers"]
    await WsConnection.broadcast(
        subscribers[symbol],
        "market.quote.updated",
        {
            "symbol": symbol,
            "price": price,
        },
    )
