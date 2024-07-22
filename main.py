import os

import azure.cognitiveservices.speech as speechsdk
import dotenv
import ffmpeg
from flask import Flask, render_template, request, jsonify

dotenv.load_dotenv()

speech_region = os.getenv('SPEECH_REGION')
speech_key = os.getenv('SPEECH_API_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def index():
    return render_template('index.html')


def convert_to_pcm_wav(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le', ac=1, ar='16000').run()
    except ffmpeg.Error as e:
        print(f'An error occurred during conversion: {e}')
        raise


@app.route('/upload', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Save the file to a temporary location
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        # Define the path for the converted file
        converted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'converted_{file.filename}')

        # Convert the file to PCM WAV format
        try:
            convert_to_pcm_wav(file_path, converted_file_path)
        except Exception as e:
            return jsonify({"error": f"Conversion failed: {str(e)}"}), 500

        # Configure Azure Speech service
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        audio_config = speechsdk.AudioConfig(filename=converted_file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Recognize speech from the audio file
        result = speech_recognizer.recognize_once()

        # Clean up the files
        os.remove(file_path)
        os.remove(converted_file_path)
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return jsonify({'transcript': result.text})
        else:
            return jsonify({'error': result.reason}), 500


if __name__ == '__main__':
    app.run(debug=True)
