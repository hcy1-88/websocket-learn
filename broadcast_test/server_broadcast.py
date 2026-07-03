import asyncio

import websockets


connected_clients = set()  # 存储已连接的客户端

async def handler(websocket):
    connected_clients.add(websocket)  # 将新连接的客户端添加到集合中
    print(f"新客户端连接: {websocket.remote_address}, 当前连接数: {len(connected_clients)}")
    try:
        async for message in websocket:
            print(f"收到消息：{message} , 广播给 {len(connected_clients)} 个客户端")
            # 广播消息给所有已连接的客户端
            await asyncio.gather(
                *(
                    client.send(f"广播消息: {message}") 
                    for client in connected_clients.copy()
                    # if client != websocket  # 是否也广播自己，看业务场景
                )
            )
    except Exception as e:
        print(f"客户端 {websocket.remote_address} 连接异常: {e}")
    finally:
        # 我按 ctrl + c，print 输出：客户端断开连接: ('::1', 58403, 0, 0), close_code=1000, close_reason=
        print(
        f"客户端断开连接: {websocket.remote_address}, "
        f"close_code={websocket.close_code}, "
        f"close_reason={websocket.close_reason}"
    )
        connected_clients.discard(websocket)  # 移除断开连接的客户端

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket 服务启动在 ws://localhost:8765")
        # 永不退出
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())