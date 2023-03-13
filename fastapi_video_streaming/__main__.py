import argparse

import uvicorn
import yaml

from fastapi_video_streaming.app import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera_profiles_yaml", "-c", type=str)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    with open(args.camera_profiles_yaml) as f:
        camera_profiles = yaml.safe_load(f)
    app = create_app(camera_profiles=camera_profiles)
    uvicorn.run(app, host="0.0.0.0")
