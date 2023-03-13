import fastapi
import fastapi.templating as templating

from fastapi_video_streaming.video_sources import VideoSourceFactory

app = fastapi.FastAPI()
templates = templating.Jinja2Templates(directory="fastapi_video_streaming/templates")


@app.get("/")
async def read_root(
    request: fastapi.Request,
    width: int = 720,
    image_provider_keys: list[str] = ["cam1", "cam2"],
):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "width": width,
            "image_provider_keys": image_provider_keys,
        },
    )


@app.get("/video_stream/{image_provider_key}")
async def stream(image_provider_key: str, width: int = 720):
    video_source = VideoSourceFactory.create_camera(
        image_provider_key=image_provider_key, width=width
    )
    return fastapi.responses.StreamingResponse(
        video_source.stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
