import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()


class AzureSpeechTranscribe:
    def __init__(self, api_key: str, region: str, audio_file_path: str):
        self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        self.audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=self.audio_config)

    def transcribe(self):
        result = self.speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f'Transcript: {result.text}')
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print('No speech could be recognized')
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails.from_result(result)
            print(f'Speech Recognition canceled: {cancellation_details.reason}')
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f'Error details: {cancellation_details.error_details}')


def test_transcriber():
    speech_key = os.environ['SPEECH_API_KEY']
    service_region = os.environ['SPEECH_REGION']
    audio_file_path = os.path.expanduser('~/repos/canto/uploads/converted_audio.wav')
    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"The audio file does not exist at {audio_file_path}")
    api = AzureSpeechTranscribe(speech_key, service_region, audio_file_path)
    api.transcribe()
