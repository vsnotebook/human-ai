def transcribe_gcs_with_word_time_offsets(
    audio_uri: str,
) -> speech.RecognizeResponse:
    """Transcribe the given audio file asynchronously and output the word time
    offsets.
    Args:
        audio_uri (str): The Google Cloud Storage URI of the input audio file.
            E.g., gs://[BUCKET]/[FILE]
    Returns:
        speech.RecognizeResponse: The response containing the transcription results with word time offsets.
    """
    from google.cloud import speech

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=audio_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_word_time_offsets=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    result = operation.result(timeout=90)

    for result in result.results:
        alternative = result.alternatives[0]
        print(f"Transcript: {alternative.transcript}")
        print(f"Confidence: {alternative.confidence}")

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time

            print(
                f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
            )

    return result
