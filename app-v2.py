"""
A sample Hello World server with FastAPI and Google Cloud Speech-to-Text v2 integration.
"""
import os
import io
import uuid
from typing import Annotated

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import speech_v2 as speech
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account

# pylint: disable=C0103
app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Google Cloud Speech-to-Text v2 setup
# PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
PROJECT_ID = "human-ai-454609"
LOCATION = "global"  # Or your preferred location
# CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
CREDENTIALS_PATH = "human-ai-454609-bf84b910d612.json"


os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

if not PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set.")
if not CREDENTIALS_PATH:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable must be set.")

credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
client = speech.SpeechClient(credentials=credentials)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": message,
            "Service": service,
            "Revision": revision,
        },
    )


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language_code: Annotated[str, Form()] = "en-US",
    model: Annotated[str, Form()] = "latest_long",
):
    """
    Transcribes audio from an uploaded file using Google Cloud Speech-to-Text v2.

    Args:
        file: The audio file to transcribe.
        language_code: The language code of the audio (e.g., "en-US").
        model: The model to use for transcription (e.g., "latest_long").

    Returns:
        A JSON response containing the transcription result.
    """
    try:
        # Check file type
        if not file.content_type.startswith("audio/"):
            return JSONResponse(
                content={"error": "Invalid file type. Only audio files are allowed."},
                status_code=400,
            )

        # Read audio data
        audio_content = await file.read()

        # Configure request
        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[language_code],
            model=model,
        )
        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{PROJECT_ID}/locations/{LOCATION}/recognizers/_",
            config=config,
            content=audio_content,
        )

        # Perform transcription
        response = client.recognize(request=request)

        # Extract transcription results
        transcription = ""
        for result in response.results:
            for alternative in result.alternatives:
                transcription += alternative.transcript

        return {"transcription": transcription}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """
    Return the audio upload page.
    """
    return templates.TemplateResponse("transcribe-audio.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    server_port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=server_port)