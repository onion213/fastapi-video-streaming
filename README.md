# fastapi-video-streaming
Very simple video streaming with FastAPI.

# Usage
1. Prepare any VideoSource (TIS Camera or MP4 File)
    - TIS Camera
        connect camera to server
    - MP4 File
        save files in local storage
2. Create camera profile file.
    
    imitate to `camera_profiles_sample.yaml`.

3. Create venv
    ```
    $ python -m venv .venv
    $ source ./.venv/bin/activate
    $ pip install -r requirements.txt
    ```
4. Start service
    ```
    $ python fastapi_video_streaming -c 
    ```
5. Access `http://localhost:8000/` via browser.
6. To see smaller/bigger images, use query parameters.
    e.g. access `http://localhost:8000/?width=360` or `http://localhost:8000/?width=3960`