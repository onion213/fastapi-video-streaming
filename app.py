import os

import cv2
import fastapi
import fastapi.templating as templating

app = fastapi.FastAPI()
templates = templating.Jinja2Templates(directory="templates")
video_path = "video.mp4"
jpeg_quality = 85


@app.get("/")
async def read_root(request: fastapi.Request, width: int = 720):
    return templates.TemplateResponse(
        "index.html", context={"request": request, "width": width}
    )


@app.get("/video_stream/{video_name}")
async def stream(video_name: str, width: int = 720):
    return fastapi.responses.StreamingResponse(
        Video(video_name).stream(width=width),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


class Video:
    def __init__(self, video_name: str):
        video_path = f"videos/{video_name}.mp4"
        self.video = cv2.VideoCapture(video_path)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, img = self.video.read()
        if not ret:
            raise Exception
        return img

    def stream(self, width):
        while True:
            cv2_img = self.get_frame()

            h, w = cv2_img.shape[:2]
            height = round(h * (width / w))
            cv2_img = cv2.resize(cv2_img, dsize=(width, height))
            ret, jpeg = cv2.imencode(
                ".jpg", cv2_img, (cv2.IMWRITE_JPEG_QUALITY, jpeg_quality)
            )
            frame = jpeg.tobytes()
            yield b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
