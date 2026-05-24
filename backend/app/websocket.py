from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):

        self.active_connections = []

        self.online_users = []


    async def connect(
        self,
        websocket: WebSocket,
        username: str
    ):

        await websocket.accept()

        self.active_connections.append(websocket)

        self.online_users.append(username)

        await self.broadcast({
            "type": "users",
            "users": self.online_users
        })


    def disconnect(
        self,
        websocket: WebSocket,
        username: str
    ):

        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if username in self.online_users:
            self.online_users.remove(username)


    async def broadcast(
        self,
        message: dict
    ):

        disconnected = []

        for connection in self.active_connections:

            try:

                await connection.send_json(message)

            except:

                disconnected.append(connection)

        for connection in disconnected:

            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()