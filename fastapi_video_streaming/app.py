import fastapi
import fastapi.templating as templating

from fastapi_video_streaming.video_sources import VideoFile

app = fastapi.FastAPI()
templates = templating.Jinja2Templates(directory="fastapi_video_streaming/templates")
jpeg_quality = 85


@app.get("/")
async def read_root(request: fastapi.Request, width: int = 720):
    return templates.TemplateResponse(
        "index.html", context={"request": request, "width": width}
    )


@app.get("/video_stream/{video_name}")
async def stream(video_name: str, width: int = 720):
    return fastapi.responses.StreamingResponse(
        VideoFile(video_name).stream(width=width),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
