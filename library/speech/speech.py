import os

import azure.cognitiveservices.speech as speechsdk
import ffmpeg
from dotenv import load_dotenv

load_dotenv()


class AzureSpeechTranscribe:
    def __init__(self, api_key, region, audio_file_path, target_language='en'):
        self.region = region
        self.api_key = api_key
        self.speech_translation_config = speechsdk.translation.SpeechTranslationConfig(subscription=api_key,
                                                                                       region=region)
        self.speech_translation_config.speech_recognition_language = 'en-US'
        self.speech_translation_config.add_target_language(target_language)
        self.audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        self.translation_recognizer = speechsdk.translation.TranslationRecognizer(
            translation_config=self.speech_translation_config, audio_config=self.audio_config)

        self.speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)

    def transcribe(self):
        result = self.translation_recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.TranslatedSpeech:
            return result.translations[self.speech_translation_config.target_languages[0]]
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise Exception('No speech could be recognized')
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            raise Exception(
                f'Speech Recognition canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}'
            )

    # def synthesize_speech(self, text, language='en'):
    #     self.speech_config.speech_synthesis_language = language
    #     result = self.speech_synthesizer.speak_text_async(text).get()
    #     if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    #         print("Speech synthesized for text [{}]".format(text))
    #     elif result.reason == speechsdk.ResultReason.Canceled:
    #         cancellation_details = speechsdk.CancellationDetails(result)
    #         print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    #         print("Error details: {}".format(cancellation_details.error_details))

    def synthesize_speech(self, text, language='en', output_path=None):
        self.speech_config.speech_synthesis_language = language
        result = self.speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))

            if output_path:
                # Expand user directory path
                output_path = os.path.expanduser(output_path)

                # Ensure the directory exists
                output_dir = os.path.dirname(output_path)
                os.makedirs(output_dir, exist_ok=True)

                try:
                    # Write the audio data to the file
                    with open(output_path, 'wb') as audio_file:
                        audio_file.write(result.audio_data)
                    print(f"Audio saved to {output_path}")
                except Exception as e:
                    print(f"Failed to save audio: {e}")

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speechsdk.CancellationDetails(result)
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            print("Error details: {}".format(cancellation_details.error_details))

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
    target_language = 'yue'  # Set the target language code for Cantonese

    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"The audio file does not exist at {audio_file_path}")

    api = AzureSpeechTranscribe(speech_key, service_region, audio_file_path, target_language)

    print(api.is_pcm_wav(audio_file_path))

    translated_text = api.transcribe()
    print(f"Translated Text: {translated_text}")

    # Synthesize the translated text into speech
    api.synthesize_speech(translated_text, language='yue', output_path='~/repos/canto/uploads/synthesized_audio.wav')
