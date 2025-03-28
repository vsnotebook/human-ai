from google.cloud import speech_v2 as speech
from google.oauth2 import service_account

from src.core.config import settings


def init_speech_client():
    if not settings.PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set.")
    if not settings.CREDENTIALS_PATH:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable must be set.")

    credentials = service_account.Credentials.from_service_account_file(settings.CREDENTIALS_PATH)
    return speech.SpeechClient(credentials=credentials)


speech_client = init_speech_client()
