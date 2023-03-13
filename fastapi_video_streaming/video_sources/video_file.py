import cv2
import multiprocessing

from fastapi_video_streaming.video_sources.video_source import VideoSource


class VideoFile(VideoSource):
    def __init__(
        self, image_provider_key: str, width: int = 720, jpeg_quality: int = 85
    ):
        super().__init__(
            image_provider_key=image_provider_key,
            width=width,
            jpeg_quality=jpeg_quality,
        )
        video_path = f"fastapi_video_streaming/videos/{image_provider_key}.mp4"
        self.cap = cv2.VideoCapture(video_path)

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, img = self.cap.read()
        if not ret:
            raise Exception
        return img
