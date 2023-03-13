import enum

import fastapi
import fastapi.templating as templating

from fastapi_video_streaming.video_sources import VideoSourceFactory


def create_app(camera_profiles: dict, allowed_widths: list = (360, 720)):
    ImageProviderKeys = enum.Enum(
        "ImageProviderKeys",
        {
            p["image_provider_key"]: p["image_provider_key"]
            for p in camera_profiles.values()
        },
    )
    AllowedWidths = enum.Enum("AllowedWidths", {w: w for w in allowed_widths})
    app = fastapi.FastAPI()
    templates = templating.Jinja2Templates(
        directory="fastapi_video_streaming/templates"
    )

    @app.get("/")
    async def read_root(
        request: fastapi.Request,
        width: int = 720,
        image_provider_keys: list[str] = ["cam1"],
    ):
        return templates.TemplateResponse(
            "index.html",
            context={
                "request": request,
                "width": width,
                "image_provider_keys": image_provider_keys,
            },
        )

    @app.get("/video_stream/{image_provider_key}/{width}")
    async def stream(image_provider_key: ImageProviderKeys, width: AllowedWidths = 720):
        video_source = VideoSourceFactory.create_camera(
            image_provider_key=image_provider_key, width=width
        )
        return fastapi.responses.StreamingResponse(
            video_source.stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    return app
