import os

import azure.cognitiveservices.speech as speechsdk
import ffmpeg
from dotenv import load_dotenv

load_dotenv()


class AzureSpeechTranscribe:
    def __init__(self, api_key, region, audio_file_path):
        self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        self.audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config,
                                                            audio_config=self.audio_config)

    def transcribe(self):
        result = self.speech_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise Exception('No speech could be recognized')
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            raise Exception(
                f'Speech Recognition canceled: {cancellation_details.reason}. Error details: {cancellation_details}'
            )

    def is_pcm_wav(self, file_path):
        """Check if the audio file is already in the correct format."""
        try:
            probe = ffmpeg.probe(file_path)
            streams = probe.get('streams', [])
            for stream in streams:
                if stream.get('codec_type') == 'audio':
                    if (stream.get('codec_name') == 'pcm_s16le' and
                            stream.get('sample_rate') == '16000' and
                            stream.get('channels') == 1):
                        return True
            return False
        except ffmpeg.Error as e:
            print(f'Error probing file format: {e}')
            raise


def test_transcriber():
    speech_key = os.environ['SPEECH_API_KEY']
    service_region = os.environ['SPEECH_REGION']
    audio_file_path = os.path.expanduser('~/repos/canto/uploads/audio.wav')
    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"The audio file does not exist at {audio_file_path}")
    api = AzureSpeechTranscribe(speech_key, service_region, audio_file_path)
    print(api.is_pcm_wav(audio_file_path))
    print(api.transcribe())
