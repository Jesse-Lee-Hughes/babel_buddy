"""
https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/

"""
import os

import azure.cognitiveservices.speech as speechsdk


class AzureSpeechToText:
    def __init__(self, subscription_key, region):
        self.subscription_key = subscription_key
        self.region = region
        self.speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.region)
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=self.audio_config
        )

    def transcribe(self):
        print("Speak into your microphone.")
        result = self.speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(result.text))
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))


if __name__ == "__main__":
    subscription_key = os.environ['SPEECH_API_KEY']
    region = os.environ['SPEECH_REGION']
    assert subscription_key
    assert region
    azure_speech_to_text = AzureSpeechToText(subscription_key, region)
    azure_speech_to_text.transcribe()
