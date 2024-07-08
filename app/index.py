from fastapi import FastAPI, Request, WebSocket, HTTPException

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import *
from .database import engine
from .routers import users
from .routers import videos
from models.connectionManager import ConnectionManager
from app import schemas
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging


Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost/",
    "http://localhost:8000",
    "http://localhost:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

app.include_router(users.router)
app.include_router(videos.router)
app.include_router(schemas.router)
templates = Jinja2Templates(directory="templates")
app.mount("/statics", StaticFiles(directory="statics"), name="statics")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
manager = ConnectionManager()


@app.websocket("/ws/{client_id}/{room}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, room: str):
    await manager.connect(room, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            logging.info(f"Received data in room {room}: {data}")
            await manager.broadcast(room, data)
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)