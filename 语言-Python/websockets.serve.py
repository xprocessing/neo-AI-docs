# 安装依赖：pip install websockets
import asyncio
import websockets

async def handle_connection(websocket):
    print('浏览器已连接')
    try:
        # 接收浏览器消息
        async for message in websocket:
            print('收到浏览器消息：', message)
            # 发送响应
            await websocket.send(f'Python已收到：{message}')
    except websockets.exceptions.ConnectionClosed:
        print('浏览器已断开连接')

async def main():
    async with websockets.serve(handle_connection, 'localhost', 8765):
        await asyncio.Future()  # 保持服务运行

if __name__ == '__main__':
    asyncio.run(main())