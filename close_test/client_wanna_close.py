import asyncio

import websockets


def state_text(websocket):
    return "关闭" if websocket.state.name == "CLOSED" else "开启"


async def client():
    async with websockets.connect("ws://localhost:8767") as websocket:
        # 检测初始状态
        print(f"初始连接状态：{state_text(websocket)}")
        while True:
            message = input("请输入消息（输入 'close' 发送关闭指令）：")
            # 发送关闭指令，服务端会主动关闭本客户端的 ws 连接
            await websocket.send(message)

            # 等待服务端完成关闭握手
            if message == "close":
                await websocket.wait_closed()
                print(f"发送关闭指令后状态：{state_text(websocket)}")
                print(f"关闭码：{websocket.close_code}，关闭原因：{websocket.close_reason}")
                break


if __name__ == "__main__":
    asyncio.run(client())