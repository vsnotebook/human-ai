# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
import os

# <code>
import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified endpoint and subscription key.
# Replace with your own endpoint and subscription key.
# speech_key, speech_endpoint = os.environ.get('SPEECH_KEY'), "https://YourServiceRegion.api.cognitive.microsoft.com"
speech_key, speech_endpoint = os.environ.get('SPEECH_KEY'), "https://southeastasia.api.cognitive.microsoft.com/"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

print("Say something...")


# Starts speech recognition, and returns after a single utterance is recognized. The end of a
# single utterance is determined by listening for silence at the end or until a maximum of about 30
# seconds of audio is processed.  The task returns the recognition text as result.
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query.
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.
result = speech_recognizer.recognize_once()

# Checks result.
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized: {}".format(result.no_match_details))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
# </code>
