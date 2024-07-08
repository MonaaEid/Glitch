from fastapi.templating import Jinja2Templates
from fastapi import Request, middleware
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import libtorrent as lt
import os
import time
from fastapi.staticfiles import StaticFiles
from app.index import ConnectionManager
from starlette.authentication import requires
from starlette.responses import RedirectResponse
import asyncio
import aiofiles


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/statics", StaticFiles(directory="statics"), name="statics")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

router = APIRouter()
if not os.path.exists("/downloads"):
    os.mkdir("/downloads")
TORRENT_DOWNLOAD_PATH = "./downloads"
TORRENT_DOWNLOAD_PATH2 ="/downloads/test.mp4"
async def get_file_path_from_torrent(torrent):
    """Get the path of the video file in the torrent."""
    file_content = await torrent.read()
    info = lt.torrent_info(file_content)
    video_file = None
    file_index = -1
    for idx, file in enumerate(info.files()):
        if file.path.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')):
            video_file = os.path.join(TORRENT_DOWNLOAD_PATH, file.path)
            file_index = idx
            break

    if file_index == -1:
        raise ValueError('No video files found in the torrent')
    return video_file


def download_torrent(torrent):
    """Download a torrent file and stream its video file as soon as it's available."""
    ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
    temp_file_path = os.path.join(TORRENT_DOWNLOAD_PATH, 'temp.torrent')
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(torrent)


    info = lt.torrent_info(temp_file_path)
    h = ses.add_torrent({'ti': info, 'save_path': TORRENT_DOWNLOAD_PATH})


    h.set_sequential_download(True)

    s = h.status()
    print('Starting', s.name)


    video_file = None
    file_index = -1
    for idx, file in enumerate(info.files()):
        if file.path.endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')):
            video_file = os.path.join(TORRENT_DOWNLOAD_PATH, file.path)
            file_index = idx
            break

    file_first_piece = info.map_file(file_index, 0, 0).piece
    file_last_piece = info.map_file(file_index, info.files().file_size(file_index), 0).piece
    for piece in range(file_first_piece, file_last_piece + 1):
        h.piece_priority(piece, 7)  # Set high priority for pieces of the video file

    print(f'Video file: {video_file}')

    print('Downloading and streaming...')
    while not os.path.exists(video_file) or os.path.getsize(video_file) == 0:
        s = h.status()
        print(f'\rProgress: {s.progress * 100:.2f}%', end='')
        time.sleep(1)

    print(f'\nVideo file available for streaming: {video_file}')

    while not s.is_seeding:
        s = h.status()
        print(f'\rProgress: {s.progress * 100:.2f}%', end='')
        time.sleep(1)

    print('\nDownload complete')


async def file_streamer(file_path: str, chunk_size: int = 1024 * 1024):
    """Stream a video file."""
    async with aiofiles.open(file_path, 'rb') as f:
        while True:
            chunk = await f.read(chunk_size)
            if not chunk:
                break
            yield chunk

@requires('authenticated', redirect='/login')
@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "name": "FastAPI"})

@router.get("/video/", response_class=HTMLResponse)
async def video(request: Request):
    return templates.TemplateResponse("stream.html", {"request": request, "name": "FastAPI"})

manager = ConnectionManager()

@router.post("/join-party/", response_class=HTMLResponse)
async def join_party(request: Request, room: str=Form(...)):
    return templates.TemplateResponse("join.html", {"request": request, "name": "FastAPI", "room": room})


@router.post("/stream/", response_class=HTMLResponse)
async def stream_torrent(request: Request, file: UploadFile = File(...)):
    try:

        file_contents = await file.read()
        await file.seek(0)
        asyncio.create_task(download_torrent(file_contents))
        await asyncio.sleep(15)
        file_location = await get_file_path_from_torrent(file)
        await asyncio.sleep(15)
        return templates.TemplateResponse("video.html", {"request": request, "filepath": file_location})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
