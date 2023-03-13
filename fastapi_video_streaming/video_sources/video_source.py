import multiprocessing


import cv2
import numpy as np


class VideoSource:
    def __init__(
        self, image_provider_key: str, width: int = 720, jpeg_quality: int = 85
    ) -> None:
        self.image_provider_key = image_provider_key
        original_height, original_width = self.get_frame_size()
        self.stream_dsize = (width, round(original_height * (width / original_width)))
        self.jpeg_quality = jpeg_quality

    def get_frame(self):
        raise NotImplementedError

    def get_frame_size(self):
        frame = self.get_frame()
        return frame.shape[:2]

    def stream(self):
        while True:
            frame = self.get_frame()
            frame = cv2.resize(frame, dsize=self.stream_dsize)
            ret, encoded_frame = cv2.imencode(
                ".jpg", frame, (cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality)
            )
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
