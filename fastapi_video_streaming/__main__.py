import uvicorn

from fastapi_video_streaming.app import app


if __name__ == "__main__":
    uvicorn.run(app)
