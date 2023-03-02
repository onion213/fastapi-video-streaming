# fastapi-video-streaming
Very simple video streaming with FastAPI.

# Usage
1. Prepare any mp4 videos and save them in `videos/`.
2. Modify `src` of `img` tags in `templates/index.html` according to the video names.
3. Create venv
    ```
    $ python -m venv .venv
    $ source ./.venv/bin/activate
    $ pip install -r requirements.txt
    ```
4. Start service with `uvicorn`.
    ```
    $ uvicorn app:app --reload
    ```
5. Access `http://localhost:8000/` via browser.
6. To see smaller/bigger images, use query parameters.
    e.g. access `http://localhost:8000/?width=360` or `http://localhost:8000/?width=3960`