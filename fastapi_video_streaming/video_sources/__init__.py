import yaml

from fastapi_video_streaming.video_sources.video_source import VideoSource
from fastapi_video_streaming.video_sources.video_file import VideoFile
from fastapi_video_streaming.video_sources.tis_camera import TisCamera


class VideoSourceFactory:
    @classmethod
    def create_camera(
        self,
        image_provider_key: str,
        width: int = 720,
        jpeg_quality: int = 85,
        **kwargs,
    ) -> VideoSource:
        if image_provider_key[:3] == "video":
            return VideoFile(
                image_provider_key=image_provider_key,
                width=width,
                jpeg_quality=jpeg_quality,
            )
        if image_provider_key[:3] == "cam":
            with open("./default_tis_config.yaml") as f:
                default_config = yaml.safe_load(f)
            return TisCamera(
                image_provider_key=image_provider_key,
                width=width,
                jpeg_quality=jpeg_quality,
                config=kwargs.get("config", default_config),
            )
        raise NotImplementedError(
            f"Unexpected `image_provider_key`: {image_provider_key}"
        )
