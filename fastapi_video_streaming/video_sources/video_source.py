import cv2


class VideoSource:
    def __init__(self, jpeg_quality: int = 85):
        self.jpeg_quality = jpeg_quality

    def get_frame(self):
        raise NotImplementedError

    def stream(self, width):
        while True:
            cv2_img = self.get_frame()

            h, w = cv2_img.shape[:2]
            height = round(h * (width / w))
            cv2_img = cv2.resize(cv2_img, dsize=(width, height))
            ret, jpeg = cv2.imencode(
                ".jpg", cv2_img, (cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality)
            )
            frame = jpeg.tobytes()
            yield b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"


class VideoFile(VideoSource):
    def __init__(self, video_name: str):
        super().__init__()
        video_path = f"fastapi_video_streaming/videos/{video_name}.mp4"
        self.video = cv2.VideoCapture(video_path)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, img = self.video.read()
        if not ret:
            raise Exception
        return img


class TisCamera(VideoSource):
    pass
