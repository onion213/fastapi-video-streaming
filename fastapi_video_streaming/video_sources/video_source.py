import multiprocessing


import cv2
import numpy as np


class VideoSource:
    def __init__(self, image_provider_key: str) -> None:
        self.image_provider_key = image_provider_key

    def get_frame(self):
        raise NotImplementedError

    def stream(self):
        while True:
            frame = self.get_frame()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )
