import os

import azure.cognitiveservices.speech as speechsdk
import ffmpeg
from dotenv import load_dotenv

load_dotenv()


class UnsupportedFileType(Exception):
    pass


class AzureSpeechTranscribe:
    def __init__(self, api_key: str, region: str, audio_file_path: str, input_language: str, output_language: str):
        self.region = region
        self.api_key = api_key
        self.speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=api_key,
                                                                                       region=region)
        self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)

        self.speech_translation_config.speech_recognition_language = input_language
        self.speech_translation_config.add_target_language(output_language)
        self.audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        self.translation_recognizer = speechsdk.translation.TranslationRecognizer(
            translation_config=self.speech_translation_config, audio_config=self.audio_config)

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)

    def transcribe(self):
        result = self.translation_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.TranslatedSpeech:
            # Print available translations for debugging
            print(f"Available translations: {result.translations}")

            # Check if the output language is in the translations
            target_language = self.speech_translation_config.target_languages[0]
            if target_language in result.translations:
                return result.translations[target_language]
            else:
                raise Exception(f"Target language {target_language} not found in translations.")
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise Exception('No speech could be recognized')
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            raise Exception(
                f'Speech Recognition canceled: {cancellation_details.reason}. '
                f'Error details: {cancellation_details.error_details}'
            )

    def synthesize_speech(self, text, target_language, output_path=None):
        self.speech_config.speech_synthesis_language = target_language
        result = self.speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for text [{text}]")

            if output_path:
                output_path = os.path.expanduser(output_path)
                output_dir = os.path.dirname(output_path)
                os.makedirs(output_dir, exist_ok=True)

                try:
                    with open(output_path, 'wb') as audio_file:
                        audio_file.write(result.audio_data)
                    print(f"Audio saved to {output_path}")
                except Exception as e:
                    print(f"Failed to save audio: {e}")

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            print(f"Error details: {cancellation_details.error_details}")

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
    input_language = 'en-US'
    output_language = 'fr'
    voice_name = 'fr-FR-HenriNeural'  # Example: French (France) - Henri Neural
    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"The audio file does not exist at {audio_file_path}")

    api = AzureSpeechTranscribe(
        speech_key,
        service_region,
        audio_file_path,
        input_language=input_language,
        output_language=output_language,
    )

    if not api.is_pcm_wav(audio_file_path):
        raise UnsupportedFileType("File type is not supported.")

    translated_text = api.transcribe()
    print(f"Translated Text: {translated_text}")

    # Synthesize the translated text into speech using 'yue' for Cantonese
    api.synthesize_speech(
        translated_text,
        target_language=output_language,
        output_path='~/repos/canto/uploads/synthesized_audio.wav'
    )


[]

if __name__ == '__main__':
    test_transcriber()
