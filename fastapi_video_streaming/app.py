import enum

import fastapi
import fastapi.templating as templating

from fastapi_video_streaming.video_sources import VideoSource


def create_app(camera_profiles: dict, allowed_widths: list = [360, 720]):
    ImageProviderKeys = enum.Enum(
        "ImageProviderKeys",
        {
            p["image_provider_key"]: p["image_provider_key"]
            for p in camera_profiles.values()
        },
    )
    AllowedWidths = enum.Enum("AllowedWidths", {str(w): w for w in allowed_widths})
    app = fastapi.FastAPI()
    templates = templating.Jinja2Templates(
        directory="fastapi_video_streaming/templates"
    )
    profiles_dict = {p["image_provider_key"]: p for p in camera_profiles.values()}

    @app.get("/")
    async def read_root(
        request: fastapi.Request, width: int = 720, jpeg_quality: int = 85
    ):
        return templates.TemplateResponse(
            "index.html",
            context={
                "request": request,
                "width": width,
                "image_provider_keys": profiles_dict.keys(),
                "jpeg_quality": jpeg_quality,
            },
        )

    @app.get("/video_stream/{image_provider_key}/{width}/{jpeg_quality}")
    async def stream(
        image_provider_key: ImageProviderKeys,
        width: int = 720,
        jpeg_quality: int = 85,
    ):
        profile = profiles_dict[image_provider_key.value]
        video_source = VideoSource(
            profile=profile, width=width, jpeg_quality=jpeg_quality
        )
        return fastapi.responses.StreamingResponse(
            video_source.stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    return app
