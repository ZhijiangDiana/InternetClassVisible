from fastapi import APIRouter
from starlette.responses import HTMLResponse, StreamingResponse

video = APIRouter()

@video.get("/competition_video")
async def get_all():
    with open("static/competition_video.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# some_file_path = "static/HoYoFair2024.mp4"
#
#
# @video.get("/competition_video")
# def main():
#     def iterfile():  # (1)
#         with open(some_file_path, mode="rb") as file_like:  # (2)
#             yield from file_like  # (3)
#
#     return StreamingResponse(iterfile(), media_type="video/mp4")
