import multiprocessing


import cv2
import numpy as np


class VideoSource:
    def __init__(
        self, image_provider_key: str, width: int = 720, jpeg_quality: int = 85
    ) -> None:
        self.image_provider_key = image_provider_key
        self.stream_width = width
        self.jpeg_quality = jpeg_quality

    def get_frame(self):
        raise NotImplementedError

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
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
