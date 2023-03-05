import fastapi
import fastapi.templating as templating
import yaml

from fastapi_video_streaming.video_sources import VideoFile, TisCamera

app = fastapi.FastAPI()
templates = templating.Jinja2Templates(directory="fastapi_video_streaming/templates")
jpeg_quality = 85
with open("tis_cam_config.yaml") as f:
    cam_config = yaml.safe_load(f)
cam = TisCamera(config=cam_config)

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

@app.get("/cam_stream")
async def stream(width: int = 720):
    return fastapi.responses.StreamingResponse(
        cam.stream(width=width),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )