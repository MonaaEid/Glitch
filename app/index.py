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

def add_user_to_context(request: Request):
    return {"user": request.state.user}

templates.env.globals['add_user_to_context'] = add_user_to_context

# sessions = {}

# async def broadcast(session_id, message):
#     for client in sessions.get(session_id, []):
#         await client.send_text(message)

@app.websocket("/ws/{client_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")

            action_timestamp = data.split(':')
            if len(action_timestamp) == 2:
                action, timestamp = action_timestamp
                timestamp = float(timestamp)
                if action == "play":
                    await manager.send_play(timestamp)
                elif action == "pause":
                    await manager.send_pause(timestamp)
                elif action == "seek":
                    await manager.send_seek(timestamp)
                else:
                    await manager.send_error_message("Invalid data format", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)