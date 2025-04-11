import os

import azure.cognitiveservices.speech as speechsdk
subscription=os.environ.get('SPEECH_KEY')
region=os.environ.get('SPEECH_REGION')
def from_mic():
    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    print(speech_recognition_result.text)

from_mic()

