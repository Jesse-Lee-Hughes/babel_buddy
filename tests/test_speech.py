import os
from library.speech import  SpeechSynthesizer, SpeechTranscriber, UnsupportedFileType
def test_transcriber():
    speech_key = os.environ['SPEECH_API_KEY']
    service_region = os.environ['SPEECH_REGION']
    audio_file_path = os.path.expanduser('~/repos/canto/uploads/audio.wav')
    input_language = 'en-US'
    output_language = 'fr'
    if not os.path.isfile(audio_file_path):
        raise FileNotFoundError(f"The audio file does not exist at {audio_file_path}")

    transcibe_api = SpeechTranscriber(
        speech_key,
        service_region,
        audio_file_path,
        input_language=input_language,
        output_language=output_language,
    )
    speech_api = SpeechSynthesizer(speech_key, service_region)
    if not speech_api.is_pcm_wav(audio_file_path):
        raise UnsupportedFileType("File type is not supported.")

    translated_text = transcibe_api.transcribe()
    print(f"Translated Text: {translated_text}")

    # Synthesize the translated text into speech using 'yue' for Cantonese
    speech_api.synthesize_speech(
        translated_text,
        target_language=output_language,
        output_path='~/repos/canto/uploads/synthesized_audio.wav'
    )


if __name__ == '__main__':
    test_transcriber()