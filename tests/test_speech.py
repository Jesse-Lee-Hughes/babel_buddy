import os
import unittest

from library.speech import SpeechSynthesizer, SpeechTranscriber, UnsupportedFileType


class TestSpeech(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize class-level variables
        cls.speech_key = os.environ.get('SPEECH_API_KEY')
        cls.service_region = os.environ.get('SPEECH_REGION')
        cls.input_language = 'en-US'
        cls.output_language = 'yue'
        cls.audio_file_path = os.path.expanduser('audio_files/audio.wav')

        # Initialize APIs
        cls.speech_api = SpeechSynthesizer(cls.speech_key, cls.service_region)
        cls.transcribe_api = SpeechTranscriber(
            cls.speech_key,
            cls.service_region,
            cls.audio_file_path,
            input_language=cls.input_language,
            output_language=cls.output_language,
        )

    def test_get_voices(self):
        r = self.speech_api.speech_synthesizer.get_voices_async().get()
        for voice in r.voices:
            print(voice.name)

    def test_transcriber(self):

        if not os.path.isfile(self.audio_file_path):
            raise FileNotFoundError(f"The audio file does not exist at {self.audio_file_path}")

        if not self.speech_api.is_pcm_wav(self.audio_file_path):
            raise UnsupportedFileType("File type is not supported.")

        translated_text = self.transcribe_api.transcribe()
        self.transcribe_api.logger.debug(f"Translated Text: {translated_text}")

        # Synthesize the translated text into speech using 'yue' for Cantonese
        self.speech_api.synthesize_speech(
            translated_text,
            target_language=self.output_language,
            output_path='audio_files/synthesized_audio.wav'
        )
