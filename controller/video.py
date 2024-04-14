from fastapi import APIRouter
from starlette.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response
from fastapi import Header
from fastapi.templating import Jinja2Templates

video = APIRouter()


@video.get("/site")
async def get_all():
    with open("static/competition_video.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# CHUNK_SIZE = 1024*1024*16
# video_path = Path("static/HoYoFair2024.mp4")
#
#
# @video.get("/stream_video")
# async def video_endpoint(range: str = Header(None)):
#     start, end = range.replace("bytes=", "").split("-")
#     start = int(start)
#     end = int(end) if end else start + CHUNK_SIZE
#     with open(video_path, "rb") as video:
#         video.seek(start)
#         data = video.read(end - start)
#         filesize = str(video_path.stat().st_size)
#         headers = {
#             'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
#             'Accept-Ranges': 'bytes'
#         }
#         return Response(data, status_code=206, headers=headers, media_type="video/mp4")
