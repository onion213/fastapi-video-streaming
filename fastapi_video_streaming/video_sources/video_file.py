import cv2

from fastapi_video_streaming.video_sources.base_capture import BaseCapture


class Mp4File(BaseCapture):
    def __init__(self, profile: dict):
        self.video_path = profile["path"]
        self.cap = cv2.VideoCapture(self.video_path)

    def __del__(self):
        self.cap.release()

    def read(self):
        ret, img = self.cap.read()
        if not ret:
            self.cap = cv2.VideoCapture(self.video_path)
            ret, img = self.cap.read()
            if not ret:
                raise Exception("Unexpected error in capturing frame from mp4 file.")
        return img
