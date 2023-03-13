import multiprocessing
from multiprocessing.managers import DictProxy
import time

import cv2

from fastapi_video_streaming.video_sources.base_capture import BaseCapture
from fastapi_video_streaming.video_sources.tis_camera import TisCameraCapture
from fastapi_video_streaming.video_sources.video_file import Mp4File


class CaptureFactory:
    @classmethod
    def create_capture(cls, profile) -> BaseCapture:
        if "model" not in profile.keys():
            raise ValueError(f"`model` is required for camera profile")

        if profile["model"] == "tis":
            return TisCameraCapture(profile)
        if profile["model"] == "mp4":
            return Mp4File(profile=profile)

        raise ValueError(f"Unknown model for camera profile: {profile['model']}")


def start_capture(profile: dict, latest_frame_dict: DictProxy):
    cap = CaptureFactory.create_capture(profile=profile)
    while True:
        latest_frame_dict[profile["image_provider_key"]] = cap.read()
        time.sleep(1 / 10)


class VideoSource:
    latest_frame_dict = None

    @classmethod
    def set_latest_frame_dict(cls):
        if cls.latest_frame_dict is None:
            cls.latest_frame_dict = multiprocessing.Manager().dict()

    def __init__(
        self,
        profile: dict,
        width: int = 720,
        jpeg_quality: int = 85,
    ) -> None:
        self.set_latest_frame_dict()
        self.image_provider_key = profile["image_provider_key"]
        self.stream_width = width
        self.jpeg_quality = jpeg_quality
        if self.image_provider_key not in VideoSource.latest_frame_dict.keys():
            VideoSource.latest_frame_dict[self.image_provider_key] = None
            p = multiprocessing.Process(
                target=start_capture,
                args=(profile, VideoSource.latest_frame_dict),
            )
            p.start()

    def get_frame(self):
        frame = None
        while frame is None:
            time.sleep(1 / 1000)
            frame = VideoSource.latest_frame_dict[self.image_provider_key]
        return frame

    def get_frame_size(self):
        frame = self.get_frame()
        return frame.shape[:2]

    def stream(self):
        original_height, original_width = self.get_frame_size()
        stream_dsize = (
            self.stream_width,
            round(original_height * (self.stream_width / original_width)),
        )
        while True:
            frame = self.get_frame()
            frame = cv2.resize(frame, dsize=stream_dsize)
            ret, encoded_frame = cv2.imencode(
                ".jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality)
            )
            encoded_frame_bytes = encoded_frame.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + encoded_frame_bytes + b"\r\n\r\n"
            )
