from fastapi import WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List


app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_play(self, session_id: str, timestamp: float):
        await self.broadcast(f"play:{timestamp}")

    async def send_pause(self, session_id: str, timestamp: float):
        await self.broadcast(f"pause:{timestamp}")

    async def send_seek(self, session_id: str, timestamp: float):
        await self.broadcast(f"seek:{timestamp}")         

# manager = ConnectionManager()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.broadcast(data)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
# '''///////////////////////////////////////////////////////////'''

# from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
# from sqlalchemy.orm import Session
# from . import models, crud, schemas
# from .database import SessionLocal, engine
# import json

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # WebSocket for signaling
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             message = json.loads(data)
            
#             # Extract relevant fields for the signaling message
#             sdp = message.get('sdp', None)
#             candidate = message.get('candidate', None)
#             sdp_mid = message.get('sdpMid', None)
#             sdp_mline_index = message.get('sdpMLineIndex', None)
            
#             signaling_message = schemas.SignalingMessageCreate(
#                 session_id=1,  # Replace with actual session ID
#                 message_type=message['type'],
#                 sdp=sdp,
#                 candidate=candidate,
#                 sdp_mid=sdp_mid,
#                 sdp_mline_index=sdp_mline_index
#             )
#             crud.create_signaling_message(db, signaling_message)
            
#             # Broadcast the message to other peers
#             await manager.broadcast(json.dumps(message))
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
