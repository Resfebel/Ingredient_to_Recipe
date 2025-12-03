from typing import Dict
from fastapi import WebSocket


# 전체적인 연결을 관리합니다
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    # 유저 이름으로 구분하니까!
    # 연결
    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        print(f"{username}님 연결되었습니다.")

    # 해제
    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
            print(f"{username}님 연결이 해제되었습니다.")

    # 특정인에게 메세지
    async def send_message(self, username: str, message: str):
        if username in self.active_connections:
            await self.active_connections[username].send_text(message)

manager = ConnectionManager()